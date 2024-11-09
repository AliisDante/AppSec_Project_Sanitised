// make api requests functions
async function getReportIds(username){
    let reportIds = [];
    reportIdsResponse = await fetch("http://127.0.0.1:5000/calculator/api/v2/report/username/"+username);
    reportIds = await reportIdsResponse.json();
    return reportIds["ids"];
}

let emissionTracker = {
    food:{
        highest: 0,
        highestItem: "",
        total:0
    },
    shopping:{
        highest: 0,
        highestItem: "",
        total:0
    },
    transport:{
        highest: 0,
        highestItem: "",
        total:0
    },
    weekly: [0,0,0,0]
}

async function getReportData(reportIds){
    let i = 1;

    last_week = (Math.floor((new Date().getTime() - new Date(0).getTime()) / 604800000)%4)+1
    target_week = 0

    while (i <= 4){
        console.log(`week ${i} ${reportIds[i-1]}`);
        target_week = ((i+last_week)%4);

        if (target_week == 0){
            target_week = 4;
        }

        if (reportIds[target_week-1].search("-0") == -1){
            reportDataResponse = await fetch("http://127.0.0.1:5000/calculator/api/v2/report/id/"+reportIds[target_week-1]);
            reportData = await reportDataResponse.json();
            console.log(reportData);
    
            if (reportData.status != "invalid, can't find report"){
    
                let foodData = reportData.categories.food
                let transportData = reportData.categories.transport
                let shoppingData = reportData.categories.shopping
        
                // weekly total
                emissionTracker.weekly[i-1] += foodData["total emission"];
                emissionTracker.weekly[i-1] += transportData["total emission"];
                emissionTracker.weekly[i-1] += shoppingData["total emission"];
        
                // add to cat total
                console.log(foodData["total emission"],transportData["total emission"])
                emissionTracker.food.total += foodData["total emission"];
                emissionTracker.transport.total += transportData["total emission"];
                emissionTracker.shopping.total += shoppingData["total emission"];
        
                // check if new high
                // for food
                if (emissionTracker.food.highest < foodData["highest emission"]){
                    emissionTracker.food.highestItem = foodData["highest item"]
                    emissionTracker.food.highest = foodData["highest emission"]
                }
                // for transport
                if (emissionTracker.transport.highest < transportData["highest emission"]){
                    emissionTracker.transport.highestItem = transportData["highest item"]
                    emissionTracker.transport.highest = transportData["highest emission"]
                }
                // for shopping
                if (emissionTracker.shopping.highest < shoppingData["highest emission"]){
                    emissionTracker.shopping.highestItem = shoppingData["highest item"]
                    emissionTracker.shopping.highest = shoppingData["highest emission"]
                }
            }
        }


        i++;
    }

    return [
        [emissionTracker.transport.highestItem, emissionTracker.food.highestItem, emissionTracker.shopping.highestItem], // highest from each cat item
        emissionTracker.weekly, // emission bar weekly
        [emissionTracker.transport.total, emissionTracker.food.total, emissionTracker.shopping.total] // by cat
    ]
}

// format data functions

// generate charts functions
// data is [int, int, int, int]
function generateEmissionBar(data){
    const emissionBar = document.getElementById('emission-bar');
    new Chart(emissionBar.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['4 week ago', '3 week ago', '2 week ago', '1 week ago'],
          datasets: [{
            label: 'emissions (in tons)',
            data: data,
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
    });
}

// data is [int, int, int]
function generateProgressPie(data){
    const progressPie = document.getElementById('progress-pie');
    new Chart(progressPie.getContext('2d'), {
        type: 'pie',
        data: {
            labels: [
              'Transport',
              'Food',
              'Shopping'
            ],
            datasets: [{
              label: 'emission by category',
              data: data,
              backgroundColor: [
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)',
                'rgb(255, 205, 86)'
              ],
              hoverOffset: 4
            }]
        },
        options: {
            scales: {
                y: {
                beginAtZero: true
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
