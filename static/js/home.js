function logout(){
    $.getJSON({
        url: "/login-cb", data: {'buttonState': 'Logout'}, success: () => {
            window.location.href = "/login";
        }
    })
}