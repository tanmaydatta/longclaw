window.fbAsyncInit = function() {
    FB.init({
        appId: app_id,
        xfbml: true,
        version: 'v2.4'
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

var signinapp = angular.module("sign_in", ["ngCookies"]);
signinapp.controller("formctrl", ['$scope', '$http', '$element', '$cookies',
    function($scope, $http, $element, $cookies) {
        var form_element = $($element);
        // $scope.uname = "";
        // $scope.passw = "";
        $scope.isInvalid = function() {
            return !($('#form').form('validate form'));
        }
        $scope.form_validate = function() {
            if (this.isInvalid()) {
                return;
            }
            this.login();
        }
        $scope.login = function() {
            $('#form').addClass('loading');
            var dataObj = {
                user: $scope.uname,
                passwd: $scope.passwd,
                'g-recaptcha-response': $('#g-recaptcha-response').val(),
            };
            $http({
                method: 'POST',
                url: '/signin/',
                data: dataObj, // pass in data as strings
            }).success(function(data) {
                $('#form').removeClass('loading');
                console.log(data);
                if (data['status'] != 'success') {

                    // if not successful, bind errors to error variables
                    $('#form').addClass('error');
                    $('#form').removeClass('loading');

                    $('.ui.error.message').html('<ul class="list"><li>' + data['msg'] + '</li></ul>');
                    grecaptcha.reset();
                } else {
                    // if successful, bind success message to message
                    // alert('success');
                    $cookies.put('auth_key', data['auth_key'], {
                        'path': '/'
                    });
                    $(location).attr('href', '/profile/' + data['user'] + '/');
                }

            });
        }
    }
]);

signinapp.controller("signwithfb", ['$scope', '$http', '$cookies',
    function($scope, $http, $cookies) {
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
                alert('h');
                this.signwithfb(response);
            } else {
                this.fb_login();
                // The person is not logged into Facebook, so we're not sure if
                // they are logged into this app or not.
            }
        }
        $scope.checkLoginState = function() {
            $('#form').addClass('loading');
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
                FB.api('/me?fields=email', function(response) {
                    if (response && !response.error) {
                        $scope.dataObj['fb_email'] = response['email'];

                        $http({
                            method: 'POST',
                            url: '/signin/facebook/',
                            data: $scope.dataObj, // pass in data as strings
                        }).success(function(data) {
                            $('#form').removeClass('loading');
                            console.log(data);
                            if (data['status'] != 'success') {
                                // if not successful, bind errors to error variables
                                $('#form').addClass('error');
                                $('#form').removeClass('loading');

                                $('.ui.error.message').html('<ul class="list"><li>' + data['msg'] + '</li></ul>');
                            } else {
                                $cookies.put('auth_key', data['auth_key'], {
                                    'path': '/'
                                });
                                $(location).attr('href', '/profile/' + data['user'] + '/');
                            }
                        });
                    }
                });
            } else {
                console.log(response);
            }
        }
    }

]);
$('#form').form({
    user: {
        identifier: 'user',
        rules: [{
            type: 'empty',
            prompt: 'Please enter a username'
        }, {
            type: 'regExp[/^[a-zA-Z0-9_-]{4,16}$/]',
            prompt: 'Please enter a 4-16 letter username with a-z 0-9 _-'
        }]
    },
    passwd: {
        identifier: 'passwd',
        rules: [{
            type: 'empty',
            prompt: 'Please enter password'
        }, {
            type: 'minLength[6]',
            prompt: 'Your password must be at least 6 characters'
        }]
    }
});
    $(document).ready(function() {
        $("#forgot").click(function() {
            $('#modaldiv').modal('show');

        });
    });
