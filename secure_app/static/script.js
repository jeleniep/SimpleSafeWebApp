function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

window.onload = () => {
  const login = document.getElementById("login");
  const password = document.getElementById("password");
  const form = document.getElementById("loginForm");
  login.addEventListener("input", checkLogin);
  console.log(form)
  form.addEventListener("submit", function(e) {
   // e.preventDefault();
    // window.location.href = "test.php";
  });



  async function checkLogin() {
    if (login.value.length <= 12 && login.value.length >= 3) {
      try {
        let url = 'http://localhost:5000/';
        const response = await fetch(url);
        console.log(response)
        if (response.status === 200) {
          if (!document.getElementById('loginError')) {
            login.insertAdjacentHTML('afterend', '<label class="error" id="loginError">Wybrany login jest już zajęty</div>');
            inputCorrectMap['login'] = false;
          }
        } else if (document.getElementById('loginError')) {
          document.getElementById('loginError').remove();
          inputCorrectMap['login'] = true;
        } 
      } catch (err) {
        inputCorrectMap['login'] = true;
      }
    } else {
      if (document.getElementById('loginError')) {
        document.getElementById('loginError').remove();
      }
      login.insertAdjacentHTML('afterend', '<label class="error" id="loginError">Login musi mieć długość pomiędzy 3 a 12 znaków.</div>');
      inputCorrectMap['login'] = false;
    }
  }


}