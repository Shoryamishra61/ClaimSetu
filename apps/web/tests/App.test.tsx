import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import type { CustodyCase } from "../src/custodyApi";
import { LangProvider } from "../src/i18n/LangProvider";

class FakeWebSocket {
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent<string>) => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: (() => void) | null = null;

  close(): void {}
}

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function renderApp() {
  return render(
    <LangProvider>
      <App />
    </LangProvider>,
  );
}

const baseCase: CustodyCase = {
  simulation: true,
  fictional: true,
  case_id: "case-ui-test",
  vehicle_no: "DL-1CA-1234",
  chassis_suffix: "56789",
  seller_id: "seller-01",
  seller_name: "Demo Seller 01 (fictional)",
  seller_address: "Demo address 01, Fictional City",
  vehicle_make: "Aster 110 Demo Scooter",
  chassis_no: "DEMOCHASSIS56789",
  engine_or_motor_no: "DEMOENGINE00001",
  rto_jurisdiction: "Registering Authority DL-01 (fictional)",
  dealer_id: null,
  dealer_name: null,
  dealer_gstin: null,
  trade_certificate_no: null,
  dealer_business_address: null,
  authorisation_certificate_no: null,
  authorisation_issued_by: null,
  authorisation_valid_until: null,
  state: "INITIATED",
  odometer_reading: null,
  delivery_timestamp: null,
  form_29c_storage_url: null,
  is_government_acknowledgement: false,
  created_at: "2026-08-22T10:00:00Z",
  updated_at: "2026-08-22T10:00:00Z",
};

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("Handover29C journey", () => {
  it("blocks the private-buyer route instead of reusing Form 29C", async () => {
    const user = userEvent.setup();
    renderApp();
    await user.click(screen.getByRole("button", { name: /selling to a private buyer/i }));
    expect(screen.getByRole("heading", { name: /different process/i })).toBeTruthy();
    expect(screen.getByText(/must not be reused for a private sale/i)).toBeTruthy();
  });

  it("switches critical interface copy and the document language to Hindi", async () => {
    const user = userEvent.setup();
    renderApp();
    await user.click(screen.getByRole("button", { name: "हिन्दी" }));
    expect(document.documentElement.lang).toBe("hi");
    expect(screen.getByRole("heading", { name: "डीलर को वाहन सुपुर्दगी" })).toBeTruthy();
    expect(screen.getByText(/सरकारी एकीकरण सिम्युलेटेड हैं/)).toBeTruthy();
  });

  it("completes all four states and exposes only a prototype PDF", async () => {
    vi.stubGlobal("WebSocket", FakeWebSocket);
    let current: CustodyCase = baseCase;
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/vehicle/verify?")) {
        return jsonResponse({
          data: {
            simulation: true,
            fictional: true,
            vehicle_id: "vehicle-01",
            vehicle_no: "DL-1CA-1234",
            chassis_suffix: "56789",
            seller_id: "seller-01",
            owner_name: "Demo Seller 01 (fictional)",
            model: "Aster 110 Demo Scooter",
            hypothecation_active: false,
          },
        });
      }
      if (url.endsWith("/case/initiate")) return jsonResponse({ case: current }, 201);
      if (url.endsWith("/dealer/verify")) {
        return jsonResponse({
          data: {
            simulation: true,
            fictional: true,
            dealer_id: "dealer-01",
            trade_certificate_no: "TC-DEL-9988",
            gstin: "07AAAAA1111A1Z1",
            business_name: "Suresh Auto (fictional)",
            rto_jurisdiction_code: "DL-14",
            status: "ACTIVE",
            can_continue: true,
          },
        });
      }
      if (init?.method === "PATCH") {
        const body = JSON.parse(String(init.body)) as { state: string };
        current = body.state === "DEALER_SELECTED"
          ? {
              ...current,
              state: "DEALER_SELECTED",
              dealer_id: "dealer-01",
              dealer_name: "Suresh Auto (fictional)",
              dealer_gstin: "07AAAAA1111A1Z1",
              trade_certificate_no: "TC-DEL-9988",
              updated_at: "2026-08-22T10:01:00Z",
            }
          : {
              ...current,
              state: "CUSTODY_TRANSFERRED",
              odometer_reading: 12345,
              delivery_timestamp: "2026-08-22T10:02:00Z",
              form_29c_storage_url: "/api/v1/cases/case-ui-test/form29c.pdf",
              updated_at: "2026-08-22T10:02:00Z",
            };
        return jsonResponse({ case: current });
      }
      if (url.includes("/cases/case-ui-test/custody")) return jsonResponse({ case: current });
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const user = userEvent.setup();
    renderApp();
    await user.click(screen.getByRole("button", { name: /handing it to an authorised dealer/i }));
    await user.click(screen.getByRole("button", { name: /use demo vehicle/i }));
    expect(screen.getByLabelText(/registration plate/i)).toHaveProperty("value", "DL-1CA-1234");
    await user.click(screen.getByRole("button", { name: /verify and continue/i }));

    expect(await screen.findByRole("heading", { name: /select the fictional dealer/i })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: /use demo dealer/i }));
    await user.click(screen.getByRole("button", { name: /verify dealer/i }));

    expect(await screen.findByRole("heading", { name: /record the physical handover/i })).toBeTruthy();
    await user.type(screen.getByLabelText(/odometer reading/i), "12345");
    const confirmations = screen.getAllByRole("checkbox");
    fireEvent.click(confirmations[0]!);
    fireEvent.click(confirmations[1]!);
    await user.click(screen.getByRole("button", { name: /confirm handover/i }));

    expect(await screen.findByRole("heading", { name: /prototype custody record prepared/i })).toBeTruthy();
    expect(screen.getByText(/not a portal acknowledgement/i)).toBeTruthy();
    const link = screen.getByRole("link", { name: /download prototype form 29c pdf/i });
    expect(link.getAttribute("href")).toBe("/api/v1/cases/case-ui-test/form29c.pdf");
    await waitFor(() => expect(sessionStorage.getItem("h29c.custody.case.v1")).toBe("case-ui-test"));
  });
});
