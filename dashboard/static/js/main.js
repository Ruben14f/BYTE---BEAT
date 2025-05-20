document.addEventListener("DOMContentLoaded", async () => {
    const chartDom = document.getElementById("chart");
    const chartDom2 = document.getElementById("chart2");
    const chartDom3 = document.getElementById("chart3");
    const chartDom4 = document.getElementById("chart4");

    const myChart = echarts.init(chartDom);
    const myChart2 = echarts.init(chartDom2);
    const myChart3 = echarts.init(chartDom3);
    const myChart4 = echarts.init(chartDom4);

    async function cargarGraficos(filtro = '') {
        myChart.showLoading();
        myChart2.showLoading();
        myChart3.showLoading();
        myChart4.showLoading();
        
        try {
            const url1 = filtro ? `/admin-dashboard/api/get-chart/?range=${filtro}` : '/admin-dashboard/api/get-chart/';
            const url2 = filtro ? `/admin-dashboard/api/get-chart2/?range=${filtro}` : '/admin-dashboard/api/get-chart2/';
            const url3 = filtro ? `/admin-dashboard/api/get-chart3/?range=${filtro}` : '/admin-dashboard/api/get-chart3/';
            const url4 = filtro ? `/admin-dashboard/api/get-chart4/?range=${filtro}` : '/admin-dashboard/api/get-chart4/';

            const response1 = await fetch(url1);
            const data1 = await response1.json();
            console.log('Data chart 1:', data1);

            const response2 = await fetch(url2);
            const data2 = await response2.json();
            console.log('Data chart 2:', data2);

            const response3 = await fetch(url3);
            const data3 = await response3.json();
            console.log('Data chart 3:', data3);

            const response4 = await fetch(url4);
            const data4 = await response4.json();
            console.log('Data chart 4:', data4);

            myChart.hideLoading();
            myChart.setOption(data1);
            myChart.resize();

            myChart2.hideLoading();
            myChart2.setOption(data2);
            myChart2.resize();

            myChart3.hideLoading();
            myChart3.setOption(data3);
            myChart3.resize();

            myChart4.hideLoading();
            myChart4.setOption(data4);
            myChart4.resize();

        } catch (error) {
            myChart.hideLoading();
            myChart2.hideLoading();
            myChart3.hideLoading();
            myChart4.hideLoading();
            console.error("Error fetching chart data:", error);
        }
    }

    // Carga inicial sin filtro (todo el año)
    cargarGraficos();

    // Opcional: si tienes un selector y botón para aplicar filtro, puedes hacer esto:
    const btnFiltrar = document.getElementById('btn-filtrar');
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', () => {
            const filtro = document.getElementById('filtro').value || '';
            cargarGraficos(filtro);
        });
    }
});
