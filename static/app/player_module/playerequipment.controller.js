app.controller('PlayerEquipmentDialogController', function($rootScope, $scope, $modalInstance, $http){
    // IMPORTANT SCOPE VARIABLES
    $scope.equipments;

    // CONSTRUCTOR
    $http.get('/api/players/equipments', {cache: true}).
        then(function(response) {
            $scope.equipments = response.data;
        }, function(response) {
            alertError(response);
        });

    // LISTEN TO EVENTS // EXPOSE METHODS TO OTHER CONTROLLERS

    // STANDARD DIALOG AND OTHER EXPOSED FUNCTIONS
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    // PRIVATE METHODS

});