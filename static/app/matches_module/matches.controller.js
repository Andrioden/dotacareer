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

    WebSocketService.subscribe("MatchFound", function(match){
        addOrExtendMatch(match);
        $rootScope.$apply();
    });

    WebSocketService.subscribe("MatchFinished", function(match){
        addOrExtendMatch(match);
        $rootScope.$apply();
    });

    // PRIVATE FUNCTIONS
    function addOrExtendMatch(match) {
        for(var i=0; i<$rootScope.player.matches.length; i++) {
            if ($rootScope.player.matches[i].id == match.id) {
                extendObjectWithObject($rootScope.player.matches[i], match);
                return;
            }
        }
        $rootScope.player.matches.push(match);
    }

});


app.controller('MatchDialogController', function ($rootScope, $scope, $modalInstance, $http, match) {

    // IMPORTANT CONTROLLER VARIABLES
    $scope.match = match;
    $scope.bet = null;
    $scope.currentBetValue = null;

    // CONSTRUCTOR
    if (!isMatchDetailed($scope.match)) {
        $http.get('/api/matches/rest/'+match.id).
            then(function(response) {
                extendObjectWithObject($scope.match, response.data);
                initiateControllerBetObject();
                $scope.bet.currentValue = $scope.bet.value;
            }, function(response) {
                alertError(response);
            });
    }
    else initiateControllerBetObject();

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.isBettingAjaxRunning = false;

    $scope.setBet = function() {
        $scope.isBettingAjaxRunning = true;
        $http.post('/api/matches/bet', {match_id: $scope.match.id, bet: $scope.bet}).
            then(function(response) {
                extendObjectWithObject($scope.bet, response.data.bet);
                $scope.bet.currentValue = $scope.bet.value;
                $rootScope.player.cash = response.data.cash;
                $scope.isBettingAjaxRunning = false;
            }, function(response) {
                alertError(response);
                $scope.isBettingAjaxRunning = false;
            });
    }

    // PRIVATE FUNCTIONS
    function isMatchDetailed(match) {
        if(typeof match.combatants === 'undefined') return false;
        else return true;
    }

    function initiateControllerBetObject() {
        for(var i=0; i<$scope.match.bets.length; i++) {
            if ($scope.match.bets[i].player.id == $rootScope.player.id) {
                $scope.bet = $scope.match.bets[i];
                return;
            }
        }
        $scope.bet = {id: null, value: 0, currentValue: 0};
        $scope.match.bets.push($scope.bet);
    }

});