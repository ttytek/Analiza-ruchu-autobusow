data_download.py: pobiera na żywo dane o położeniach autobusów przez godzine i zapisuje do pliku (przykładowy plik vehicle_data_evening.json)
timetable_download.py: pobiera rozkłady przyjazdów autobusów dla wszystkich przystanków i dzieli je wzglądem autobusów które przyjeżdżają na te przystanki (przykładowy plik przystanki.json, zzipowany do przystanki.zip)
analyze_data.py: analizuje pobrane dane o autobusach (wyniki dla przykładowych danych: analysis.out , figure[1-5].png)
profiler.py: analizuje dane zebrane przy odpaleniu programu z profilerem (przykładowy wynik w pliku profiler_results.out)
setup.py: pozwala na zainstalowanie kodu jako pakietu przy pomocy pip install
prof.sh: polecenie analizujące kod profilerem (tworzy plik profile_results.prof)
