import { Component } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {catchError, Observable, of} from "rxjs";
import {AlertService} from "../services";
import {ModelMetadata} from "../models";

@Component({
  selector: 'app-guest-page',
  templateUrl: './guest-page.component.html',
  styleUrls: ['./guest-page.component.css']
})
export class GuestPageComponent {
  private readonly SERVER_URL = 'http://127.0.0.1:5000';
  private readonly SERVER_METADATA_ROUTE = '/pretrained_models_metadata'
  private readonly SERVER_SUBMIT_GUEST_QUERY_ROUTE = '/submit/guest_query'

  private metadata: Map<string, ModelMetadata> = new Map<string, ModelMetadata>();
  private selected_pretrained_model = '';
  private natural_language_query = '';

  private table_schema_file: File | null = null;

  constructor(private httpClient: HttpClient,
              private alertService: AlertService) {}

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
    const url = this.SERVER_URL + this.SERVER_SUBMIT_GUEST_QUERY_ROUTE;

    if (!this.table_schema_file || !model_dir || this.natural_language_query === '') {
      this.alertService.error('No query, pretrained model, or file selected.');
      return;
    }

    const form_data: FormData = new FormData();
    form_data.append('file', this.table_schema_file);
    form_data.append('natural_language_query', this.natural_language_query);
    form_data.append('pretrained_model', model_dir);

    this.httpClient.post<any>(url, form_data).pipe(catchError(this.handleError<undefined>('onSubmitQueryButton', undefined))).subscribe(
      (result) => {
        result = result['query'];

        const text_to_sql_result_input = document.getElementById('text_to_sql_result') as HTMLInputElement;
        text_to_sql_result_input.value = result;
      }
    );
  }

  private getModelDirFromName(name: string): string | null {
    let model_dir = null;
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
            this.alertService.error(error);

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }
}
