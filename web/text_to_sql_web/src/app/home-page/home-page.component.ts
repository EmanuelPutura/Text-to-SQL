import {Component, ViewChild} from '@angular/core';
import {AccountService, AlertService} from "../services";
import {ModelMetadata} from "../../../../sqlgen_web/src/app/domain/model_metadata";
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {catchError, map, Observable, of} from "rxjs";

@Component({ templateUrl: 'home-page.component.html' })
export class HomePageComponent {
  private readonly SERVER_URL = 'http://127.0.0.1:5000';
  private readonly SERVER_METADATA_ROUTE = '/pretrained_models_metadata'
  private readonly SERVER_USER_TABLES_SCHEMAS = '/user_table_schemas'
  private readonly SERVER_SUBMIT_HOME_QUERY_ROUTE = '/submit/home_query'
  private readonly SERVER_SUBMIT_SCHEMA_ROUTE = '/submit/schema'

  private metadata: Map<string, ModelMetadata> = new Map<string, ModelMetadata>();
  private selected_pretrained_model = '';
  private natural_language_query = '';
  private selected_table_schema = '';
  private table_schema_file: File | null = null;
  private table_schemas: string[] = [];

  constructor(private httpClient: HttpClient,
              private alertService: AlertService,
              private accountService: AccountService) {}

  ngOnInit(): void {
    this.fetchPretrainedModelsMetadata().subscribe((metadata) => {
      this.metadata = new Map(Object.entries(metadata));
    });

    this.fetchUserTableSchemas().subscribe((schemas) => {
      this.table_schemas = schemas;
    });
  }

  getModelsMetadataList() {
    return Array.from(this.metadata.values());
  }

  get tableSchemas() {
    return this.table_schemas;
  }

  set selectedPretrainedModel(pretrained_model: string) {
    this.selected_pretrained_model = pretrained_model;
  }

  set selectedTableSchema(table_schema: string) {
    this.selected_table_schema = table_schema;
  }

  set naturalLanguageQuery(query: string) {
    this.natural_language_query = query;
  }

  onFileSelected(event: any) {
    this.table_schema_file = event.target.files[0];
  }

  onSubmitQueryButton(): void {
    const model_dir = this.getModelDirFromName(this.selected_pretrained_model)
    const url = this.SERVER_URL + this.SERVER_SUBMIT_HOME_QUERY_ROUTE;

    if (!this.selected_table_schema || !model_dir || this.natural_language_query === '') {
      this.alertService.error('No query, pretrained model, or table schema selected.');
      return;
    }

    const form_data: FormData = new FormData();
    form_data.append('natural_language_query', this.natural_language_query);
    form_data.append('pretrained_model', model_dir);
    form_data.append('table_schema_name', this.selected_table_schema);

    this.httpClient.post<any>(url, form_data).pipe(catchError(this.handleError<undefined>('onSubmitQueryButton', undefined))).subscribe(
      (result) => {
        result = result['query'];

        const text_to_sql_result_input = document.getElementById('text_to_sql_result') as HTMLInputElement;
        text_to_sql_result_input.value = result;
      }
    );
  }

  onSubmitTableSchemaButton(): void {
    const url = this.SERVER_URL + this.SERVER_SUBMIT_SCHEMA_ROUTE;
    const username = this.accountService.userValue?.username;

    if (!this.table_schema_file || !username) {
      this.alertService.error('No table schema file selected or invalid username.');
      return;
    }

    const form_data: FormData = new FormData();
    form_data.append('file', this.table_schema_file);
    form_data.append('username', username);

    this.httpClient.post<any>(url, form_data).pipe(catchError(this.handleError<undefined>('onSubmitTableSchemaButton', undefined)))
      .pipe(map(response => {
        const status = response['status'];

        if (status === 'table_schema_successfully_added') {
          const table_name = response['table_name'];
          const select_table_schema_element = document.getElementById('select_table_schema');

          const new_option = document.createElement('option');
          new_option.text = table_name;
          new_option.value = table_name;

          select_table_schema_element?.appendChild(new_option);
          this.selected_table_schema = table_name;
        }
      })).subscribe()
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

  private fetchUserTableSchemas(): Observable<string[]> {
    const url = this.SERVER_URL + this.SERVER_USER_TABLES_SCHEMAS + `/${this.accountService.userValue?.username}`;
    return this.httpClient.get<string[]>(url).pipe(catchError(this.handleError<string[]>('fetchUserTableSchemas', [])));
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
