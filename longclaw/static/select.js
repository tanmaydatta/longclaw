var selectapp = angular.module("select", []);

window.fbAsyncInit = function() {
    FB.init({
        appId: app_id,
        xfbml: true,
        version: 'v2.5'
    });
    // checkLoginState();
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

selectapp.controller('selectctrl', function($scope, $http) {
    // $scope.admin_token = function() {
    // alert('hello');
    $scope.dataObj = {};
    $scope.fb_login = function() {
        FB.login(function(response) {
            // handle the response
            $scope.signwithfb(response);
        }, {
            scope: 'public_profile,email,user_managed_groups'
        });
    }

    $scope.statusChangeCallback = function(response) {
        // The response object is returned with a status field that lets the
        // app know the current login status of the person.
        // Full docs on the response object can be found in the documentation
        // for FB.getLoginStatus().
        if (response.status === 'connected') {
            // Logged into your app and Facebook.
            // alert('h');  
            this.signwithfb(response);
        } else {
            this.fb_login();
            // The person is not logged into Facebook, so we're not sure if
            // they are logged into this app or not.
        }
    }
    $scope.checkLoginState = function() {
        $('#form').addClass('loading');
        // alert('h');
        FB.getLoginStatus(function(response) {
            $scope.statusChangeCallback(response);
        });
    }
    $scope.signwithfb = function(response) {
        // FB.api('/me/picture?width=400&height=400', function(response) {
        // console.log(response);
        // });
        if (response && !response.error) {
            $scope.dataObj['access_token'] = response['authResponse']['accessToken'];
            $http({
                method: 'POST',
                url: '/admin/access_token/',
                data: $scope.dataObj, // pass in data as strings
            }).success(function(data) {
                console.log(data);
            });
        } else {
            console.log(response);
        }
    }


});