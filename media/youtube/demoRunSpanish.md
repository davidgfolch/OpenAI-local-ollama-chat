# Demo OpenAi local Ollama chat

En este video os voy a mostrar como usar el proyecto. Aquí no voy a explicar como instalar los requisitos necesarios (ollama y modelos, python/conda, node/yarn etc.) para ello ver el "README.md".

Empezaremos con el backend:

- activamos el entorno de conda.
- ejecutamos main.py

Seguiremos con el frontend:

- ejecutamos "yarn serve"

Una vez se haya levantado el frontend, vamos al navegador y accedemos a "localhost:8080". Al cargar la página podremos ver que da un error porque Ollama no se está ejecutando.

Este error lo podemos ver en el frontend y tambien en los logs de backend.

Levantamos el servicio ollama, y mostramos los logs. Además comprobaremos en los logs que Ollama está usando la GPU.

Una vez Ollama está ejecutándose podemos hacer nuestra pregunta al LLM (por defecto se usa el modelo Deepseek V2).

En cuanto ollama empieze a contestar podremos ver como se va escribiendo la respuesta dinamicamente (content-type=text/event-stream), así como en los logs de backend.

Eso es todo en esta demo, gracias!
