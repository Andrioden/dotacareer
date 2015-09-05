app.controller('MatchesController', function($rootScope, $scope, $modal, WebSocketService){

    // EXPOSED ACTIONS FOR HTML
    $scope.openMatchDialog = function (match) {
        var modalInstance = $modal.open({
            animation: true,
            templateUrl: 'matchDialog.html',
            controller: 'MatchDialogController',
            resolve: { // Data passed to the dialog, has to be a function. Its the angularjs pattern for it i guess
                match: function() {return match;}
            }
        });
    };

    // LISTEN TO EVENTS // EXPOSE METHODS TO OTHER CONTROLLERS
    $scope.$on('MatchesControllerEvent_OpenMatchDialog', function(event, match) {
        $scope.openMatchDialog(match);
    });

    WebSocketService.subscribe("MatchCompleted", function(match){
        $rootScope.player.matches.push(match);
        $rootScope.$apply();
    });

});


app.controller('MatchDialogController', function ($scope, $modalInstance, $http, match) {

    // IMPORTANT CONTROLLER VARIABLES
    $scope.match = match;

    // CONSTRUCTOR
    if (!isMatchDetailed($scope.match)) {
        $http.get('/api/matches/rest/'+match.id).
            then(function(response) {
                extendObjectWithObject($scope.match, response.data);
            }, function(response) {
                AlertError(response);
            });
    }

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    // PRIVATE FUNCTIONS
    function isMatchDetailed(match) {
        if(typeof match.combatants === 'undefined') return false;
        else return true;
    }

    function extendObjectWithObject(object1, object2) {
        for (var attrname in object2) { object1[attrname] = object2[attrname]; }
    }

});