import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Reserva {
  id: number;
  pais: string;
  estado: string;
  email: string;
  telefono: string;
}

@Injectable({ providedIn: 'root' })
export class ReservasService {
  private readonly RES_URL = 'http://localhost:8002';

  constructor(private http: HttpClient) {}

  getReserva(id: number): Observable<Reserva> {
    return this.http.get<Reserva>(`${this.RES_URL}/reservas/${id}`);
  }

  getReservas(): Observable<Reserva[]> {
    return this.http.get<Reserva[]>(`${this.RES_URL}/reservas`);
  }

  updateReserva(id: number, data: Partial<Reserva>): Observable<{ mensaje: string }> {
    return this.http.put<{ mensaje: string }>(`${this.RES_URL}/reservas/${id}`, data);
  }
}
