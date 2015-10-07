function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
        // Logged into your app and Facebook.
        testAPI();
    } else if (response.status === 'not_authorized') {
        // The person is logged into Facebook, but not your app.
        // document.getElementById('status').innerHTML = 'Please log ' +
        // 'into this app.';
    } else {
        // The person is not logged into Facebook, so we're not sure if
        // they are logged into this app or not.
        // document.getElementById('status').innerHTML = 'Please log ' +
        // 'into Facebook.';
    }
}
// This function is called when someone finishes with the Login
// Button.  See the onlogin handler attached to it in the sample
// code below.
function login() {
    FB.login(function(response) {
        // handle the response
    }, {
        scope: 'public_profile,email,user_managed_groups'
    });
}

function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}
window.fbAsyncInit = function() {
    FB.init({
        appId: '{{ app_id }}',
        xfbml: true,
        version: 'v2.4'
    });
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
};
// Load the SDK asynchronously
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
// Here we run a very simple test of the Graph API after login is
// successful.  See statusChangeCallback() for when this call is made.
function testAPI() {
    // console.log('Welcome!  Fetching your information.... ');
    // FB.api('/me?fields=id,name,email,permissions', function(response) {
    //   console.log('Successful login for: ' + response.email);
    //   console.log(response);
    //   // document.getElementById('status').innerHTML =
    //   //   'Thanks for logging in, ' + response.name + '!';
    // });
    FB.api('/996710020358819?fields=images', function(response) {
        // console.log('Successful login for: ' + response.email);
        console.log(response);
        // $('#fbpic').attr("src",response.data.url);
        // document.getElementById('status').innerHTML =
        //   'Thanks for logging in, ' + response.name + '!';
    }, {
        scope: 'user_managed_groups'
    });
}