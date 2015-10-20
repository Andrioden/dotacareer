app.controller('TournamentsDialogController', function($rootScope, $scope, $modalInstance, $http){
    // IMPORTANT SCOPE VARIABLES
    $scope.tournaments = [];

    $http.get('/api/tournaments/rest/').
        then(function(response) {
            $scope.tournaments = response.data;
            setIfJoinedTournaments();
        }, function(response) {
            alertError(response);
        });

    // CONSTRUCTOR

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.isJoiningTournament = false;

    $scope.joinTournament = function(tournament) {
        $scope.isJoiningTournament = true;
        $http.post('/api/tournaments/join/', {tournament_id: tournament.id}).
            then(function(response) {
                $scope.isJoiningTournament = false;
            }, function(response) {
                alertError(response);
                $scope.isJoiningTournament = false;
            });
    }

    // PRIVATE METHODS

    function setIfJoinedTournaments() {
        for (var i=0; i<$scope.tournaments.length; i++) {
            for (var p=0; p<$scope.tournaments[i].participants.length; p++) {
                var participantTeamID = $scope.tournaments[i].participants[p].id;
                if (participantTeamID == $rootScope.player.team.id) {
                    $scope.tournaments[i].hasJoined = true;
                    break;
                }
            }
        }
    }

});