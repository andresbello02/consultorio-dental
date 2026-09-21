document.addEventListener("submit", function(e) {
    if (e.target && e.target.id === "formCita") {
        e.preventDefault();

        const cita = {
            nombre: document.getElementById("nombre").value,
            apellido: document.getElementById("apellido").value,
            correo: document.getElementById("correo").value,
            telefono: document.getElementById("telefono").value,
            servicio: document.getElementById("servicio").value,
            mensaje: document.getElementById("mensaje").value,
            fecha: new Date().toLocaleString()
        };

        let citas = JSON.parse(localStorage.getItem("citas")) || [];
        citas.push(cita);
        localStorage.setItem("citas", JSON.stringify(citas));

        alert("¡Datos enviados con éxito! Pronto nos comunicaremos contigo.");
        e.target.reset();
    }
});

/* ========================================= */
/* BEFORE / AFTER SLIDER */
/* ========================================= */

/* ========================================= */
/* BEFORE / AFTER PRO */
/* ========================================= */

document.addEventListener("DOMContentLoaded", ()=>{

    const slider = document.getElementById("slider");
    const afterWrapper = document.getElementById("afterWrapper");
    const sliderLine = document.querySelector(".slider-line");

    if(!slider) return;

    const updateSlider = ()=>{

        const value = slider.value;

        afterWrapper.style.width = value + "%";
        sliderLine.style.left = value + "%";
    };

    slider.addEventListener("input", updateSlider);

    updateSlider();

});

if(slider){

    slider.addEventListener("input", (e)=>{

        let value = e.target.value;

        afterWrapper.style.width = value + "%";

        sliderLine.style.left = value + "%";

    });

}

/* ========================================= */
/* AI ANALYZER */
/* ========================================= */

function openAIAnalyzer(){

    document.getElementById("aiModal").style.display = "flex";
}

function closeAIAnalyzer(){

    document.getElementById("aiModal").style.display = "none";
}

const imageUpload = document.getElementById("imageUpload");
const previewImage = document.getElementById("previewImage");
const previewContainer = document.querySelector(".preview-container");

if(imageUpload){

    imageUpload.addEventListener("change",(e)=>{

        const file = e.target.files[0];

        if(file){

            const reader = new FileReader();

            reader.onload = function(event){

                previewImage.src = event.target.result;

                previewContainer.style.display = "block";
            }

            reader.readAsDataURL(file);
        }
    });
}
