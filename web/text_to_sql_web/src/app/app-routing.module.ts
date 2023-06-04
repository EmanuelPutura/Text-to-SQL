import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {HomePageComponent} from "./home-page/home-page.component";
import {GuestPageComponent} from "./guest-page/guest-page.component";
import {AuthGuard} from "./helpers";

const accountModule = () => import('./account-page/account.module').then(x => x.AccountModule);

const routes: Routes = [
    { path: '', component: HomePageComponent, canActivate: [AuthGuard] },
    { path: 'guest', component: GuestPageComponent },
    { path: 'account', loadChildren: accountModule },

    // otherwise redirect to home
    { path: '**', redirectTo: '' }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }

