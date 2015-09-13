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
    }
]);

function alertError(response) {
    alert(response.data.message)
}

function extendObjectWithObject(object1, object2) {
    for (var attrname in object2) { object1[attrname] = object2[attrname]; }
}

app.filter('yesNo', function () {
    return function (input) {
        return input ? 'Yes' : 'No';
    }
});