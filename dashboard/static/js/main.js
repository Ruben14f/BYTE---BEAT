document.addEventListener("DOMContentLoaded", async () => {
    const chartDom2 = document.getElementById("chart2");
    const chartDom3 = document.getElementById("chart3");
    const chartDom4 = document.getElementById("chart4");

    const myChart2 = echarts.init(chartDom2);
    const myChart3 = echarts.init(chartDom3);
    const myChart4 = echarts.init(chartDom4);

    const filtroSelect = document.getElementById('filtro'); // filtro global
    const btnFiltrar = document.getElementById('btn-filtrar');
    const btnBorrarFiltro = document.getElementById('btn-borrar-filtro');

    // Filtro individual gráfico 2 (agrega estos elementos en HTML con estos IDs)
    const filtroChart2Select = document.getElementById('filtro-chart2');
    const btnFiltrarChart2 = document.getElementById('btn-filtrar-chart2');
    const btnBorrarFiltroChart2 = document.getElementById('btn-borrar-filtro-chart2');

    btnBorrarFiltro.style.display = 'none'; // ocultar botón borrar filtro global inicialmente
    if (btnBorrarFiltroChart2) btnBorrarFiltroChart2.style.display = 'none'; // ocultar botón borrar filtro 2

    async function cargarChart2(filtroGlobal = '', filtroIndividual = '') {
        myChart2.showLoading();
        try {
            let url = '/admin-dashboard/api/get-chart2/';
            const params = new URLSearchParams();

            // Prioriza filtro individual para chart 2 si existe, sino usa filtro global
            if (filtroIndividual) {
                params.append('range_chart2', filtroIndividual);
            } else if (filtroGlobal) {
                params.append('range', filtroGlobal);
            }

            if ([...params].length > 0) url += '?' + params.toString();

            const response = await fetch(url);
            const data = await response.json();

            myChart2.hideLoading();
            if (!data.series || data.series.length === 0) myChart2.clear();
            else {
                myChart2.setOption(data);
                myChart2.resize();
            }
        } catch (error) {
            myChart2.hideLoading();
            console.error("Error loading Chart 2:", error);
        }
    }

    async function cargarGraficos(filtroGlobal = '') {
        // Carga gráfico 2 con filtro global solo si no hay filtro individual
        const filtroIndChart2 = filtroChart2Select ? filtroChart2Select.value : '';
        cargarChart2(filtroGlobal, filtroIndChart2);

        // Carga otros gráficos solo con filtro global (o adapta si tienes filtros individuales)
        myChart3.showLoading();
        myChart4.showLoading();

        try {
            const url3 = filtroGlobal ? `/admin-dashboard/api/get-chart3/?range=${filtroGlobal}` : '/admin-dashboard/api/get-chart3/';
            const url4 = filtroGlobal ? `/admin-dashboard/api/get-chart4/?range=${filtroGlobal}` : '/admin-dashboard/api/get-chart4/';

            const [response3, response4] = await Promise.all([fetch(url3), fetch(url4)]);
            const data3 = await response3.json();
            const data4 = await response4.json();

            myChart3.hideLoading();
            if (!data3.series || data3.series.length === 0) myChart3.clear();
            else {
                myChart3.setOption(data3);
                myChart3.resize();
            }

            myChart4.hideLoading();
            if (!data4.series || data4.series.length === 0) myChart4.clear();
            else {
                myChart4.setOption(data4);
                myChart4.resize();
            }
        } catch (error) {
            myChart3.hideLoading();
            myChart4.hideLoading();
            console.error("Error loading Chart 3 or 4:", error);
        }
    }

    // Eventos filtro global
    btnFiltrar.addEventListener('click', () => {
        const filtro = filtroSelect.value || '';
        cargarGraficos(filtro);
        btnBorrarFiltro.style.display = filtro ? 'inline-block' : 'none';
    });

    btnBorrarFiltro.addEventListener('click', () => {
        filtroSelect.value = '';
        btnBorrarFiltro.style.display = 'none';
        cargarGraficos('');
    });

    // Eventos filtro individual gráfico 2
    if (btnFiltrarChart2 && filtroChart2Select && btnBorrarFiltroChart2) {
        btnFiltrarChart2.addEventListener('click', () => {
            const filtro = filtroChart2Select.value || '';
            cargarChart2('', filtro);
            btnBorrarFiltroChart2.style.display = filtro ? 'inline-block' : 'none';
        });

        btnBorrarFiltroChart2.addEventListener('click', () => {
            filtroChart2Select.value = '';
            btnBorrarFiltroChart2.style.display = 'none';
            cargarChart2();
        });
    }

    // Carga inicial sin filtros
    cargarGraficos('');
});
