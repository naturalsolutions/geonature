# Documentation pour tracer frontend et backend


## Documentation frontend avec compodoc

Pour utiliser compodoc il faut lancer la commande suivante :

- `npm run compodoc:serve`

Ce script est présent dans le `package.json`.
Si la librairie compodoc n'est pas installé normalement il vous est demandé de l'installer sinon éxécuter les commandes suivantes dans votre frontend.

```sh
cd geonature/frontend
nvm use
npm install -g @compodoc/compodoc
```

Puis relancer le script pour voir la documentation : `npm run compodoc:serve`.

## Documentation pour tracing avec jaeger 

### Backend 

Il faut tout d'abord lancer jaeger dans un container docker .

```sh
docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 14250:14250 \
  -p 9411:9411 \
  jaegertracing/all-in-one:1.22
```

Une fois que le container est créé, on vérifie que Jaeger est lancé avec la commande suivante: `docker ps | grep jaeger`.
On récupère le container id et on lance ensuite :  `docker logs <container_id_jaeger>`

Ensuite il faut sourcer le venv de l'app GN : `source backend/venv/bin/activate` . Et installer les dépendances nécessaires 

`pip install jaeger-client flask_opentracing opentracing`

L'utilisation de Jaeger se fait au niveau du fichier `app.py`.

Les modifcations apportées sont les suivantes : 

```py
#app.py

from jaeger_client import Config
from flask_opentracing import FlaskTracing

# Configuration de Jaeger
def init_tracer(service_name='my-flask-app'):
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'logging': True,
            'reporter_batch_size': 1,
        },
        service_name=service_name,
        validate=True,
    )
    return config.initialize_tracer()

.....
.....
def create_app(with_external_mods=True):
    app = Flask(
        __name__.split(".")[0],
        root_path=config["ROOT_PATH"],
        static_folder=config["STATIC_FOLDER"],
        static_url_path=config["STATIC_URL"],
        template_folder="geonature/templates",
    )
    app.config.update(config)
    # Initialiser Jaeger et FlaskTracing (ces deux lignes ajoutées)
    tracer = init_tracer(service_name=app.config.get('SERVICE_NAME', 'my-flask-app'))
    tracing = FlaskTracing(tracer, True, app)


```


### Frontend

Au préalable il faut installer les dépendances coté frontend : 

`npm install @opentelemetry/instrumentation @opentelemetry/instrumentation-xml-http-request @opentelemetry/context-zone`

Coté frontend un fichier est créé à la racine du dossier `src`.

```ts
// opentelemetry-config.ts
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

```

Il faut ensuite importer ce fichier dans le `main.ts`.

```ts
//fichier main.ts
import './opentelemetry-config';  // Importez votre configuration OpenTelemetry
```

### Visualisation des traces

Pour visualiser les traces c'est normalement sur : `http://localhost:16686`.

Sinon penser à vérifier le port relié au container de jaeger : `docker ps | grep jaeger `
