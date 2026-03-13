import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { ReservasService, Reserva } from '../../services/reservas.service';

@Component({
  selector: 'app-reservas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reservas.component.html',
  styleUrl: './reservas.component.css'
})
export class ReservasComponent implements OnInit {
  reservas: Reserva[] = [];
  loadError = '';
  toast: { message: string; type: 'error' | 'success' } | null = null;

  editingId: number | null = null;
  editEmail = '';

  constructor(
    public authService: AuthService,
    private reservasService: ReservasService
  ) {}

  ngOnInit(): void {
    this.loadReservas();
  }

  loadReservas(): void {
    this.loadError = '';
    this.reservasService.getReservas().subscribe({
      next: (data) => { this.reservas = data; },
      error: (err) => {
        if (err.status === 403) {
          this.loadError = 'Acceso denegado: no tiene permiso para ver estas reservas.';
        } else {
          this.loadError = 'Error al cargar reservas.';
        }
      }
    });
  }

  startEdit(reserva: Reserva): void {
    this.editingId = reserva.id;
    this.editEmail = reserva.email;
  }

  cancelEdit(): void {
    this.editingId = null;
    this.editEmail = '';
  }

  attemptModify(reserva: Reserva): void {
    this.reservasService.updateReserva(reserva.id, { email: this.editEmail }).subscribe({
      next: () => {
        this.showToast('Reserva actualizada correctamente.', 'success');
        this.editingId = null;
        this.loadReservas();
      },
      error: (err) => {
        if (err.status === 403) {
          this.showToast('Acceso denegado (403): ' + (err.error?.mensaje ?? 'No autorizado'), 'error');
        } else {
          this.showToast('Error al modificar la reserva.', 'error');
        }
        this.editingId = null;
      }
    });
  }

  showToast(message: string, type: 'error' | 'success'): void {
    this.toast = { message, type };
    setTimeout(() => { this.toast = null; }, 4000);
  }

  crossPaisResult: { status: number; mensaje: string } | null = null;

  testCrossPais(): void {
    this.crossPaisResult = null;
    this.reservasService.getReserva(1).subscribe({
      next: (r) => {
        this.crossPaisResult = { status: 200, mensaje: `OK — se vio la reserva de ${r.pais} (acceso permitido)` };
      },
      error: (err) => {
        this.crossPaisResult = { status: err.status, mensaje: err.error?.mensaje ?? 'Acceso denegado' };
      }
    });
  }

  logout(): void {
    this.authService.logout();
  }
}
