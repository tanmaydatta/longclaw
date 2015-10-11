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
// Here we run a very simple test of the Graph API after login is
// successful.  See statusChangeCallback() for when this call is made.

knuth.controller("facebook", ['$scope', '$http',
    function($scope, $http) {
        $scope.dataObj = {};
        $scope.fb_login = function() {
            FB.login(function(response) {
                // handle the response
                sync_with_facebook();
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
                this.sync_with_facebook(response);
            } else {
                this.fb_login();
                // The person is not logged into Facebook, so we're not sure if
                // they are logged into this app or not.
            }
        }
        $scope.checkLoginState = function() {
            FB.getLoginStatus(function(response) {
                $scope.statusChangeCallback(response);
            });
        }
        $scope.sync_with_facebook = function(response) {
            // FB.api('/me/picture?width=400&height=400', function(response) {
            // console.log(response);
            // });
            if (response && !response.error) {
                $scope.dataObj['access_token'] = response['authResponse']['accessToken'];
                FB.api('/me?fields=email', function(response) {
                    if (response && !response.error) {
                        $scope.dataObj['fb_email'] = response['email'];
                        $('#sync').addClass('loading');
                        $http({
                            method: 'POST',
                            url: '/sync/' + login_user + '/',
                            data: $scope.dataObj, // pass in data as strings
                        }).success(function(data) {
                            $('#form').removeClass('loading');
                            console.log(data);
                            if (data['status'] != 'success') {
                                // if not successful, bind errors to error variables
                                $('#sync').removeClass('loading');
                                alert(data['msg']);
                            } else {
                                location.reload();
                            }
                        }).error(function(data) {
                            alert('Error');
                        });
                    }
                });
            }
        }
    }
]);


knuth.controller("settings", ['$scope', '$http',
    function($scope, $http) {
        $scope.save = function() {
            // var postData = {};
            var postData = new FormData();
            if ($scope.settings) {
                postData['settings'] = $scope.settings;
            }
            $('#settings').addClass('loading');
            $http({
                method: 'POST',
                url: '/settings/' + login_user + '/',
                data: $scope.settings, // pass in data as strings
            }).success(function(data) {
                // $('#form').removeClass('loading');
                // console.log(data);
                if (data['status'] != 'success') {
                    //     // if not successful, bind errors to error variables
                    //     $('#sync').removeClass('loading');
                        alert(data['msg']);
                        $('#settings').removeClass('loading');
                } else {
                    location.reload();
                }
            }).error(function(data) {
                alert('Error');
                $('#settings').removeClass('loading');
            });
            
            // if ($('#pic')[0].files.length == 1) {
            //     postData['pic'] = $('#pic')[0];
            // }
        }
    }
]);