$('.ui.slider.checkbox')
    .checkbox();
$('#level')
    .dropdown({
        action: 'activate',
        onChange: function(value, text, $selectedItem) {
            // custom action
            action: 'hide'

        }

        // maxSelections: 1
    });
$('#tag')
    .dropdown({
        allowAdditions: true,
        maxSelections: false
    });

var knuth = angular.module("knuth", []);
knuth.controller("markdown", ['$scope',
    function($scope) {
        $scope.toHTML = function() {
            $('#m2html').text('');
            $('#m2html').append(markdown.toHTML($scope.content.statement));

        }

        $scope.toHTML_ip = function() {
            $('#m2html_ip').text('');
            $('#m2html_ip').append(markdown.toHTML($scope.content.ip));

        }
        $scope.toHTML_op = function() {
            $('#m2html_op').text('');
            $('#m2html_op').append(markdown.toHTML($scope.content.op));

        }
        $scope.toHTML_sip = function() {
            $('#m2html_sip').text('');
            $('#m2html_sip').append(markdown.toHTML($scope.content.sip));

        }
        $scope.toHTML_sop = function() {
            $('#m2html_sop').text('');
            $('#m2html_sop').append(markdown.toHTML($scope.content.sop));

        }

         $scope.submitpro= function() {
         	console.log($scope.content);

         		// $('#form').addClass('loading');
            var dataObj = $scope.content;
            
            $http({
                method: 'POST',
                url: '/add_problem/',
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


        // $scope.content="hello";
        // $scope.content = $scope.content + 'vvv';
    }
]);
