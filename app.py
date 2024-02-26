from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
import logging
import uuid
import requests
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

metrics = PrometheusMetrics(app)

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = SimpleSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

FlaskInstrumentor().instrument_app(app)

@app.route("/")
def hello():
 
    request_id = str(uuid.uuid4())
    logger.info(f"Endpoint '/' foi acessado. Request ID: {request_id}")

    with trace.get_tracer(__name__).start_as_current_span("hello") as span:
        span.set_attribute("request_id", request_id)

@app.route("/request")
def make_request():

    request_id = str(uuid.uuid4())
    logger.info(f"Endpoint '/request' foi acessado. Request ID: {request_id}")

    with trace.get_tracer(__name__).start_as_current_span("make_request") as span:
        span.set_attribute("request_id", request_id)
   
        response = requests.get("http://localhost:5000/")
    return "Request feita para o servidor Flask!"

if __name__ == "__main__":
    app.run(debug=True)
