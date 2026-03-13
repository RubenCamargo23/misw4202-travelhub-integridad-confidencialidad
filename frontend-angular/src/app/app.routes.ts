import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { ReservasComponent } from './pages/reservas/reservas.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'reservas', component: ReservasComponent, canActivate: [authGuard] },
  { path: '', redirectTo: 'reservas', pathMatch: 'full' },
  { path: '**', redirectTo: 'reservas' }
];
