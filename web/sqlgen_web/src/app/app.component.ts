import {Component, OnInit} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {ModelMetadata} from "./domain/model_metadata";
import {catchError, Observable, of} from "rxjs";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  private readonly httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/x-www-form-urlencoded'
    })
  };

  private readonly SERVER_URL = 'http://127.0.0.1:5000';
  private readonly SERVER_METADATA_ROUTE = '/pretrained_models_metadata'
  private readonly SERVER_SUBMIT_ROUTE = '/submit'

  private metadata: Map<string, ModelMetadata> = new Map<string, ModelMetadata>();
  private selected_pretrained_model = '';
  private natural_language_query = '';

  private table_schema_file: File | null = null;

  constructor(private httpClient: HttpClient) {
  }

  ngOnInit(): void {
    this.fetchPretrainedModelsMetadata().subscribe((metadata) => {
      this.metadata = new Map(Object.entries(metadata));
    })
  }

  getModelsMetadataList() {
    return Array.from(this.metadata.values());
  }

  set selectedPretrainedModel(pretrained_model: string) {
    this.selected_pretrained_model = pretrained_model;
  }

  set naturalLanguageQuery(query: string) {
    this.natural_language_query = query;
  }

  onFileSelected(event: any) {
    this.table_schema_file = event.target.files[0];
  }

  onSubmitQueryButton(): void {
    const model_dir = this.getModelDirFromName(this.selected_pretrained_model)
    const url = this.SERVER_URL + this.SERVER_SUBMIT_ROUTE;

    if (!this.table_schema_file) {
      console.error('No file selected.');
      return;
    }

    const http_options = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };

    const form_data: FormData = new FormData();
    form_data.append('file', this.table_schema_file);
    form_data.append('natural_language_query', this.natural_language_query);
    form_data.append('pretrained_model', model_dir);

    this.httpClient.post<any>(url, form_data).pipe(catchError(this.handleError<undefined>('onSubmitQueryButton', undefined))).subscribe();
  }

  private getModelDirFromName(name: string): string {
    let model_dir = ''
    this.metadata.forEach((value, key) => {
      if (value.name === name) {
        model_dir = key;
      }
    });

    return model_dir;
  }

  private fetchPretrainedModelsMetadata(): Observable<{ [key: string]: ModelMetadata; }> {
    const url = this.SERVER_URL + this.SERVER_METADATA_ROUTE;
    return this.httpClient.get<{ [key: string]: ModelMetadata; }>(url).pipe(catchError(this.handleError<{ [key: string]: ModelMetadata; }>('fetchPretrainedModelsMetadata', {})));
  }

  /**
    * Handle the http operation that failed.
    * Let the app continue.
    * @param operation - name of the operation that failed
    * @param result - optional value to return as the observable result
    */
    private handleError<T>(operation = 'operation', result?: T) {
        return (error: any): Observable<T> => {
            // TODO: send the error to remote logging infrastructure
            console.error(error); // log to console instead

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }
}
