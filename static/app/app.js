var app = angular.module('DOTACareer', ['ui.bootstrap']);

function AlertError(response) {
    alert(response.data.message)
}