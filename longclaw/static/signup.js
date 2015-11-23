// $('#date').dateSelector();

$("#datepicker").datepicker();
$("#datepicker").datepicker("option", "showAnim", "clip");


var signupapp = angular.module("sign_up", ["ngCookies"]);
signupapp.controller("formctrl", ['$scope', '$http', '$element', '$cookies',
    function($scope, $http, $element, $cookies) {
        var form_element = $($element);
        // $scope.uname = "";
        // $scope.passw = "";
        $scope.isInvalid = function() {
            return !form_element.form('validate form');
        }
        $scope.form_validate = function() {
            if (this.isInvalid()) {
                return;
            }
            this.signup();
        }
        $scope.signup = function() {
            $('#form').addClass('loading');
            var dataObj = $scope.user;
            dataObj['g-recaptcha-response'] = $('#g-recaptcha-response').val();
            $http({
                method: 'POST',
                url: '/signup/',
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
                    $cookies.put('auth_key', data['auth_key'], {
                        'path': '/'
                    });
                    $(location).attr('href', '/');
                }

            });
        }
    }
]);

$('#form')
    .form({
        fname: {
            identifier: 'fname',
            rules: [{
                type: 'empty',
                prompt: 'Please enter your first name'
            }]
        },
        lname: {
            identifier: 'lname',
            rules: [{
                type: 'empty',
                prompt: 'Please enter your last name'
            }]
        },

        user: {
            identifier: 'user',
            rules: [{
                type: 'empty',
                prompt: 'Please enter a user name'
            }]
        },
        email: {
            identifier: 'email',
            rules: [{
                type: 'email',
                prompt: 'Please enter a valid e-mail'
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
        },
        cpasswd: {
            identifier: 'cpasswd',
            rules: [{
                type: 'match[passwd]',
                prompt: 'Passwords do not match'
            }]
        }
    });
