from http.server import BaseHTTPRequestHandler, HTTPServer
import json

hostName = "localhost"
serverPort = 8080


def diff_cum_interest(rate_per_month: float, Nper: int, Pv: float, start_period: int, end_period: int) -> float:
    """ Calculate sum of interests for differentiated payments from start_period to end_period
    """

    main_month_payment = Pv/Nper
    remainder = Pv
    sum_interests = 0
    period = 1

    while period <= end_period:

        interest_per_month = remainder*rate_per_month

        if period >= start_period:
            sum_interests += interest_per_month

        remainder -= main_month_payment
        period += 1

    return round(sum_interests, 3)


def annuity_cum_interest(rate_per_month: float, Nper: int, Pv: float, start_period: int, end_period: int) -> float:
    """ Calculate sum of interests for annuity payments from start_period to end_period
    """

    month_payment = Pv * (rate_per_month +
                          (rate_per_month / ((1+rate_per_month)**Nper-1)))

    remainder = Pv
    sum_interests = 0
    period = 1

    while period <= end_period:

        interest_per_month = remainder*rate_per_month

        if period >= start_period:
            sum_interests += interest_per_month

        remainder -= (month_payment-interest_per_month)
        period += 1

    return round(sum_interests, 3)


def unpack(params):
    rate_per_month = params["Rate_per_year"]/12
    Nper = params["Nper"]
    Pv = params["Pv"]
    start_period = params["Start_period"]
    end_period = params["End_period"]

    if start_period <= 0 or end_period <= 0:
        raise Exception('start_period and end_period must be greater 0')
    if start_period > end_period:
        raise Exception('end_period must be greater than start_period')
    if end_period > Nper:
        raise Exception('end_period must be less than Nper')
    if Pv < 0:
        raise Exception('Pv must be greater 0')
    if params['Type'] not in ['diff', 'annuity']:
        raise Exception('Unknown type of calculation interests')

    return rate_per_month, Nper, Pv, start_period, end_period


class InterestServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        params = json.loads(body.decode("utf-8"))

        try:
            rate_per_month, Nper, Pv, start_period, end_period = unpack(params)

            if params['Type'] == 'diff':
                result = diff_cum_interest(
                    rate_per_month, Nper, Pv, start_period, end_period)
            elif params['Type'] == 'annuity':
                result = annuity_cum_interest(
                    rate_per_month, Nper, Pv, start_period, end_period)

            result = json.dumps({'cum_interest': result})

        except Exception as e:
            result = json.dumps({'Error': str(e)})

        self._set_headers()
        self.wfile.write(result.encode('utf-8'))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), InterestServer)
    print("Server started on http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
