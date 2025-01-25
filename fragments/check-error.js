fetch("/_had_error").then(response => {
  if (response.status !== 404) {
    document.body.style.backgroundColor = "#ffb6c1";
  }
})
