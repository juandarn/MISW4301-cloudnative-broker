def tpl_verified(name: str | None = None, score: float | None = None, threshold: float = 60.0):
    saludo = f"Hola {name}," if name else "Hola,"
    score_txt = f"{score:.2f}" if isinstance(score, (int, float)) else "N/A"
    html = f"""
    <div style="font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif">
      <h2>✅ Verificación exitosa</h2>
      <p>{saludo}</p>
      <p>Tu identidad ha sido <strong>verificada</strong> correctamente.</p>
      <p><strong>Score de verificación:</strong> {score_txt} (umbral: {threshold:.0f})</p>
      <p>Ya puedes usar todas las funciones de la plataforma.</p>
    </div>
    """
    text = (
f"""{saludo}

Tu identidad ha sido VERIFICADA correctamente.
Score de verificación: {score_txt} (umbral: {threshold:.0f})

Ya puedes usar todas las funciones de la plataforma."""
    )
    return html, text


def tpl_not_verified(name: str | None = None, score: float | None = None, threshold: float = 60.0):
    saludo = f"Hola {name}," if name else "Hola,"
    score_line = f"(score: {score:.2f}, umbral: {threshold:.0f})" if isinstance(score, (int, float)) else "(score: N/A)"
    html = f"""
    <div style="font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif">
      <h2>⚠️ Verificación no completada</h2>
      <p>{saludo}</p>
      <p>No fue posible completar la verificación {score_line}.</p>
      <p>Puedes reintentar el proceso o contactar soporte si crees que es un error.</p>
      <ul>
        <li>Verifica que tus datos coincidan con tu documento</li>
        <li>Asegúrate de que la foto sea nítida y bien iluminada</li>
      </ul>
    </div>
    """
    text = (
f"""{saludo}

No fue posible completar la verificación {score_line}.
Puedes reintentar el proceso o contactar soporte si crees que es un error.

Sugerencias:
- Verifica que tus datos coincidan con tu documento
- Asegura buena iluminación y nitidez en la foto"""
    )
    return html, text
