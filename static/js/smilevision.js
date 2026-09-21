// Convierte un archivo File a una cadena Base64 para vista previa
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = (error) => reject(error);
    });
}

// Función principal con diseño limpio y moderno
async function analyzeSmile() {
    console.log("Cargando simulación local...");

    const fileInput = document.getElementById("imageUpload");
    const treatmentSelect = document.getElementById("tratamientoAI");
    const resultDiv = document.getElementById("aiResult");

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert("Por favor, selecciona una fotografía antes de analizar.");
        return;
    }

    if (!treatmentSelect || !treatmentSelect.value) {
        alert("Por favor, selecciona un tratamiento del menú desplegable.");
        return;
    }

    const treatmentKey = treatmentSelect.value;
    const zonaImplante = document.getElementById("zonaImplante")?.value.trim() || "";

    if (treatmentKey === "implantes" && !zonaImplante) {
        alert("Indica qué espacio dental deseas restaurar.");
        return;
    }

    if (resultDiv) {
        resultDiv.style.display = "block";
        resultDiv.innerHTML = `
            <div style="margin-top: 15px; padding: 12px; text-align: center; background: rgba(56, 189, 248, 0.08); border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2);">
                <p style="color: #38bdf8; font-weight: 500; font-size: 0.9rem; margin: 0;">✨ Generando simulación estética...</p>
            </div>
        `;
    }

    const file = fileInput.files[0];

    try {
        const imageBase64 = await fileToBase64(file);

        // Selección de la imagen predeterminada según el archivo cargado
        const nombreArchivo = file.name.toLowerCase();
        let imagenPredeterminada = "/static/IMG/paciente1_despues.jpg";

        if (nombreArchivo.includes("2") || nombreArchivo.includes("joven")) {
            imagenPredeterminada = "/static/IMG/paciente2_despues.jpg";
        } else if (nombreArchivo.includes("3") || nombreArchivo.includes("nino")) {
            imagenPredeterminada = "/static/IMG/paciente3_despues.jpg";
        }

        // Simulamos un breve retraso estético y mostramos el diseño renovado
        setTimeout(() => {
            resultDiv.innerHTML = `
                <div style="margin-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 14px;">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 12px;">
                        <span style="font-size: 1.1rem;">✨</span>
                        <h4 style="color: #38bdf8; font-weight: 600; font-size: 0.95rem; margin: 0;">Resultado de la Simulación</h4>
                    </div>
                    
                    <!-- Contenedor lado a lado para Original vs Resultado -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 8px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
                            <span style="display: block; font-size: 0.75rem; font-weight: 500; margin-bottom: 6px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Original</span>
                            <img src="${imageBase64}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);">
                        </div>
                        <div style="background: rgba(56, 189, 248, 0.05); padding: 8px; border-radius: 10px; border: 1px solid rgba(56, 189, 248, 0.2); text-align: center;">
                            <span style="display: block; font-size: 0.75rem; font-weight: 500; margin-bottom: 6px; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px;">Resultado</span>
                            <img src="${imagenPredeterminada}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.3);">
                        </div>
                    </div>

                    <!-- Cuadro de diagnóstico estilizado -->
                    <div style="background: rgba(15, 23, 42, 0.8); padding: 10px 12px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06); text-align: left;">
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                            <span style="font-size: 0.85rem;">📋</span>
                            <h5 style="color: #f8fafc; margin: 0; font-size: 0.85rem; font-weight: 600;">Diagnóstico Estándar</h5>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.8rem; line-height: 1.35; margin: 0;">Simulación procesada con éxito. Se aprecia una corrección armónica en la alineación y brillo de la sonrisa.</p>
                    </div>
                </div>
            `;
        }, 400);

    } catch (error) {
        console.error("Error:", error);
        if (resultDiv) {
            resultDiv.innerHTML = `<p style="color: #ef4444; font-size: 0.85rem; text-align: center; margin-top: 10px;">Error al cargar la imagen.</p>`;
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const selector = document.getElementById("tratamientoAI");
    const panel = document.getElementById("zonaImplantePanel");

    if (!selector || !panel) return;

    const actualizarPanel = () => {
        panel.hidden = selector.value !== "implantes";
    };

    selector.addEventListener("change", actualizarPanel);
    actualizarPanel();
});