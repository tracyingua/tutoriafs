function moveNext(index, event) {
    let input = document.getElementById(`code${index}`);
    let nextInput = document.getElementById(`code${index + 1}`);
    let prevInput = document.getElementById(`code${index - 1}`);


    if (event.inputType !== "deleteContentBackward" && input.value.length === 1 && nextInput) {
        nextInput.focus();
    } 

    
    else if (event.inputType === "deleteContentBackward" && prevInput) {
        input.value = ""; 
        prevInput.focus();
    }


    let fullCode = "";
    for (let i = 1; i <= 6; i++) {
        let digit = document.getElementById(`code${i}`).value;
        fullCode += digit ? digit : "";
    }
    document.getElementById("full_code").value = fullCode;
}
