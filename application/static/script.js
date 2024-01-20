

document.addEventListener("DOMContentLoaded", function() {
    let text = document.querySelector(".text");
    text.innerHTML=text.innerText
        .split("")
        .map((letters,i) =>
        `<span style="transition-delay:${i *80}ms;
        filter:hue-rotate(${i * 30}deg)">
        ${letters}
        </span>`
    ).join("");   
    
    text.classList.add("hovered");
    setTimeout(function(){
        text.classList.remove("hovered");
    },800)
    
    });