import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { ZipkinExporter } from '@opentelemetry/exporter-zipkin';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { ZoneContextManager } from '@opentelemetry/context-zone';

// Configure the exporter
const zipkinExporter = new ZipkinExporter({
  serviceName: 'my-angular-app',
  url: 'http://localhost:9411/api/v2/spans',  // URL de votre endpoint Jaeger/Zipkin
});

// Create a provider
const provider = new WebTracerProvider();

// Configure the provider with the exporter
provider.addSpanProcessor(new SimpleSpanProcessor(zipkinExporter));

// Register the provider globally
provider.register({
  contextManager: new ZoneContextManager(),
});

// Register instrumentations
registerInstrumentations({
  instrumentations: [
    new XMLHttpRequestInstrumentation(),
  ],
});
