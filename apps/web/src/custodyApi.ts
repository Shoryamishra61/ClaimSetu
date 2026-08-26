export type CustodyState =
  | "DRAFT"
  | "INITIATED"
  | "DEALER_SELECTED"
  | "CUSTODY_TRANSFERRED";

export interface VehicleFixture {
  simulation: true;
  fictional: true;
  vehicle_id: string;
  vehicle_no: string;
  chassis_suffix: string;
  seller_id: string;
  owner_name: string;
  owner_address: string;
  model: string;
  chassis_no: string;
  engine_or_motor_no: string;
  rto_jurisdiction: string;
  hypothecation_active: boolean;
}

export interface DealerFixture {
  simulation: true;
  fictional: true;
  dealer_id: string;
  trade_certificate_no: string;
  gstin: string;
  business_name: string;
  rto_jurisdiction_code: string;
  business_address: string;
  authorisation_certificate_no: string;
  authorisation_issued_by: string;
  authorisation_valid_until: string;
  status: "ACTIVE" | "EXPIRED" | "SUSPENDED";
  can_continue: boolean;
}

export interface CustodyCase {
  simulation: true;
  fictional: true;
  case_id: string;
  vehicle_no: string;
  chassis_suffix: string;
  seller_id: string;
  seller_name: string;
  seller_address: string;
  vehicle_make: string;
  chassis_no: string;
  engine_or_motor_no: string;
  rto_jurisdiction: string;
  dealer_id: string | null;
  dealer_name: string | null;
  dealer_gstin: string | null;
  trade_certificate_no: string | null;
  dealer_business_address: string | null;
  authorisation_certificate_no: string | null;
  authorisation_issued_by: string | null;
  authorisation_valid_until: string | null;
  state: CustodyState;
  odometer_reading: number | null;
  delivery_timestamp: string | null;
  form_29c_storage_url: string | null;
  is_government_acknowledgement: false;
  created_at: string;
  updated_at: string;
}

interface ApiFailure {
  error: {
    code: string;
    message: string;
    message_hi: string;
    recoverable: boolean;
  };
}

export class CustodyApiError extends Error {
  readonly code: string;
  readonly messageHi: string;

  constructor(code: string, message: string, messageHi: string) {
    super(message);
    this.name = "CustodyApiError";
    this.code = code;
    this.messageHi = messageHi;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/v1${path}`, {
      ...init,
      credentials: "omit",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new CustodyApiError(
      "TRANSPORT_ERROR",
      "Could not reach the prototype server. Nothing was submitted.",
      "प्रोटोटाइप सर्वर तक नहीं पहुँच सके। कुछ भी सबमिट नहीं हुआ।",
    );
  }
  const payload = (await response.json()) as unknown;
  if (!response.ok) {
    const failure = payload as ApiFailure;
    throw new CustodyApiError(
      failure.error?.code ?? "UNKNOWN_ERROR",
      failure.error?.message ?? "The prototype could not complete that step.",
      failure.error?.message_hi ?? "प्रोटोटाइप यह चरण पूरा नहीं कर सका।",
    );
  }
  return payload as T;
}

export async function verifyCustodyVehicle(
  vehicleNo: string,
  chassisSuffix: string,
): Promise<VehicleFixture> {
  const query = new URLSearchParams({ vehicle_no: vehicleNo, chassis_suffix: chassisSuffix });
  const payload = await request<{ data: VehicleFixture }>(`/vehicle/verify?${query}`);
  return payload.data;
}

export async function initiateCustodyCase(vehicle: VehicleFixture): Promise<CustodyCase> {
  const payload = await request<{ case: CustodyCase }>("/case/initiate", {
    method: "POST",
    body: JSON.stringify({
      vehicle_no: vehicle.vehicle_no,
      chassis_suffix: vehicle.chassis_suffix,
      seller_id: vehicle.seller_id,
    }),
  });
  return payload.case;
}

export async function verifyCustodyDealer(input: {
  gstin?: string;
  trade_certificate_no?: string;
}): Promise<DealerFixture> {
  const payload = await request<{ data: DealerFixture }>("/dealer/verify", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return payload.data;
}

export async function getCustodyCase(caseId: string): Promise<CustodyCase> {
  const payload = await request<{ case: CustodyCase }>(
    `/cases/${encodeURIComponent(caseId)}/custody`,
  );
  return payload.case;
}

export async function setCustodyState(
  caseId: string,
  body: Record<string, unknown>,
): Promise<CustodyCase> {
  const payload = await request<{ case: CustodyCase }>(
    `/cases/${encodeURIComponent(caseId)}/state`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
  return payload.case;
}

export function form29cUrl(caseId: string): string {
  return `/api/v1/cases/${encodeURIComponent(caseId)}/form29c.pdf`;
}
