var app = angular.module('DOTACareer', ['ngRoute', 'ui.bootstrap']);

app.config(['$routeProvider', '$locationProvider',
    function ($routeProvider, $locationProvider) {
        $routeProvider.
            when('/home', {
                templateUrl: 'static/app/home/home.view.html'
            })
            .otherwise({
                redirectTo: '/home'
            });

        $locationProvider.html5Mode(true);
    }]);

function AlertError(response) {
    alert(response.data.message)
}

app.filter('yesNo', function () {
    return function (input) {
        return input ? 'Yes' : 'No';
    }
});