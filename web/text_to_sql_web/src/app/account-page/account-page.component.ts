import { Component } from '@angular/core';
import { Router } from '@angular/router';
import {AccountService} from "../services";


@Component({ templateUrl: 'account-page.component.html' })
export class AccountPageComponent {
    constructor(
      private router: Router,
      private accountService: AccountService
    ) {
      this.router.navigate(['/']);
    }
}
