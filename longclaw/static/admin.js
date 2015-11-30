var adminapp = angular.module("admin", ["ngCookies"]);
adminapp.controller("adminctrl", ['$scope', '$http', '$element', '$cookies',
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
            this.adminlogin();
        }
        $scope.adminlogin = function() {
            $('#form').addClass('loading');
            var dataObj = $scope.user;
            $http({
                method: 'POST',
                url: '/admin/',
                data: dataObj, // pass in data as strings
            }).success(function(data) {
                $('#form').removeClass('loading');
                console.log(data);
                if (data['status'] != 'success') {

                    // if not successful, bind errors to error variables
                    $('#form').addClass('error');
                    $('.ui.error.message').html('<ul class="list"><li>' + data['msg'] + '</li></ul>');
                } else {
                    // if successful, bind success message to message
                    // alert('success');
                    $cookies.put('admin_key', data['admin_key'], {
                        'path': '/'
                    });
                    $(location).attr('href', '/select');
                }

            });
        }
    }
]);
$('#form').form({
    uname: {
        identifier: 'uname',
        rules: [{
            type: 'empty',
            prompt: 'Please enter a username'
        }, {
            type: 'regExp[/^[a-zA-Z0-9_-]{4,16}$/]',
            prompt: 'Please enter a 4-16 letter username with a-z 0-9 _-'
        }]
    },
    pwd: {
        identifier: 'pwd',
        rules: [{
            type: 'empty',
            prompt: 'Please enter password'
        }, {
            type: 'minLength[6]',
            prompt: 'Your password must be at least 6 characters'
        }]
    }
});