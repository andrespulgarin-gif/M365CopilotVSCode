# M365 Copilot completo 3.0.7 — ejecución prolongada de comandos

## Cambio solicitado

El límite de `300` segundos de `m365_run_command` era local, tanto en el esquema que ve el modelo como en `tools/terminal.ts`. El valor `3600` se reducía silenciosamente a `300`, cancelando compilaciones Maven válidas.

La **versión 3.0.7** elimina ese techo. Se conserva la implementación completa de M365CopilotVSCode (autenticación, selección de modelo, herramientas, aprobaciones y modos), sin crear otro agente.

### Semántica nueva

| `timeoutSeconds` | Tiempo concedido |
|---|---|
| Sin especificar | 60 segundos, como antes |
| `300` | 300 segundos |
| `3600` | 3600 segundos = 1 hora |
| `0` | Sin temporizador local **de comando** |

No se modifican ni los permisos/aprobaciones ni el modo de selección de modelos. La validación del parámetro ahora exige un entero no negativo; valores incorrectos producen un error explícito en lugar de ser convertidos silenciosamente.

La ejecución con la terminal integrada sigue utilizando VS Code Shell Integration. Cuando no está disponible, se utiliza la ejecución secundaria original. Ambas rutas usan el mismo temporizador cancelable; con `0` no se crea ninguno. La cancelación manual sigue funcionando y dispone/cancela el proceso o terminal como antes. Los temporizadores superiores al máximo representable por un `setTimeout` de Node.js se dividen en segmentos, evitando una terminación inmediata por desbordamiento.

### Controles que deliberadamente NO se cambiaron

- Presupuesto del chat principal: `m365copilot.chat.maxDurationMinutes` (8 min de fábrica, `0` elimina ese límite global local).
- Límite de llamadas: `m365copilot.chat.maxToolCalls` (0 = sin límite de llamadas en el participante general).
- Tiempo por respuesta remota de BizChat: 5 minutos.
- El valor predeterminado de tiempo de un comando **sin** `timeoutSeconds` explícito: 60 segundos.
- Captura de salida, límite de tamaño de comandos, reintentos y condiciones de cancelación.
- Aprobaciones de `m365_run_command` de VS Code: **se conservan**.
- Identidad M365, autenticación de navegador, herramientas, dependencias, selecciones de modelo y comandos.

`m365copilot.chat.maxDurationMinutes: 0` sigue siendo importante si se quiere continuar el análisis al terminar un comando de 40 minutos; de lo contrario, el motor puede finalizar la tarea por el presupuesto global al siguiente paso. `timeoutSeconds: 0` no cambia automáticamente esa configuración.

### Pruebas

- Sin valor: 60 segundos.
- `3600`: temporizador solicitado de 3.600.000 ms, sin recorte.
- `0`: no hay temporizador local que provoque terminación.
- Cancelación: limpia el temporizador pendiente.
- Valores mayores del máximo de `setTimeout` de Node: se dividen correctamente, sin disparo anticipado.
- Valor inválido: se rechaza en vez de convertirse silenciosamente.
- CI: typecheck, lint, build, suites de regresión y VSIX. El control de paridad compara las contribuciones completas del manifiesto con la base, neutralizando **únicamente** el cambio explícito de `timeoutSeconds`.

### Ejemplo para Maven largo

El agente puede pedir la herramienta con `timeoutSeconds: 3600`; en Windows:

```powershell
& 'C:\apache-maven-3.6.3\bin\mvn.cmd' '-Djava.version:11' -pl ejb -am -DskipTests compile
```

La cadena `-Djava.version:11` es la indicada por el usuario; la versión **real** de Java que corre Maven debe verificarse leyendo la salida de `mvn -version` o el wrapper pertinente. Una propiedad Maven `-D` no garantiza por sí sola el cambio de JVM.

### Limitaciones de validación

Las pruebas con temporizadores simulados verifican la ausencia de truncamiento a 300s y la programación correcta. No equivalen a ejecutar una compilación Maven real de 40 minutos dentro de Windows/VS Code, que sigue pendiente de observarse.

Los límites de salida del runner secundario y el timeout del servicio de modelos son independientes y se conservan.

Versión: **3.0.7**. Rama: `fix-m365-long-terminal-3-0-7`. Sin cambios a `main`. No se subió código corporativo.
