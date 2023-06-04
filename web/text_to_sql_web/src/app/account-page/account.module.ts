import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AccountRoutingModule } from './account-routing.module';
import { LoginComponent } from './login.component';
import { RegisterComponent } from './register.component';
import {AccountPageComponent} from "./account-page.component";

@NgModule({
    imports: [
        CommonModule,
        ReactiveFormsModule,
        AccountRoutingModule
    ],
    declarations: [
        AccountPageComponent,
        LoginComponent,
        RegisterComponent
    ]
})
export class AccountModule { }
