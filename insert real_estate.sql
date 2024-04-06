insert into real_estate(name, build_year, regional_code, lot_number, road_name_address, latitude, longitude, point)
values ('가나빌라', 1990, '11111', '서울특별시 서초구 반포동 715-33', '서울특별시 서초구 주흥9길 26-20 (반포동)', '37.5071287', '127.018819', ST_GeomFromText('point(37.5071287 127.018819)', 4326));

