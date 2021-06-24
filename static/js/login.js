// Login functionality
function login(){
    const uName = document.getElementById("username-in").value;
    const pwd = document.getElementById("password-in").value;
    const loginButton = document.getElementById('login-button');
    $.getJSON({
        url: "/login-cb", data: {'username': uName, 'pwd': pwd, 'buttonState': loginButton.value}, success: (res) => {
            if (res.isAuth){
                // Redirect to landing page
                window.location.href = "/";
            } else {
                // If loginButton.value was 'Logout' (i.e., was logged in, but not now), update value to login and re-pull NHP list
                if (loginButton.value === 'Logout'){
                    loginButton.value = 'Login';
                }
            }
        }
    })
}
