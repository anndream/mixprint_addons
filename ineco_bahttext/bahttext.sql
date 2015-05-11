CREATE OR REPLACE FUNCTION bahttext(i numeric) RETURNS text AS 
$$
	DECLARE
		result 		varchar(200);
		inputtext 		varchar(20);
		value ALIAS 	FOR $1;
		batharray		text array;
		stang		int;
		stang_text 	varchar(100);
		bath_text 	varchar(100);
		s1			int;
		s2			int;
		ba			int array;
		subtext		varchar(20);
		
       BEGIN
		result := '';
		subtext := '';
		stang_text := '';
		bath_text := bath_text || '';
		inputtext := value::text;
		inputtext := replace(inputtext,',','');

		batharray := regexp_split_to_array(inputtext, E'\\.');
		s1 := substring( batharray[2],1,1);
		s2 := substring( batharray[2],2,1);
		if s1 = 0 and s2 = 0 then
			subtext := 'ถ้วน';
		else
			subtext := 'สตางค์';
			if s1 = '1' then
				stang_text := '';
			elseif s1 = '2' then
				stang_text := 'ยี่';
			elseif s1 = '3' then
				stang_text := 'สาม';
			elseif s1 = '4' then
				stang_text := 'สี่';
			elseif s1 = '5' then
				stang_text := 'ห้า';
			elseif s1 = '6' then
				stang_text := 'หก';
			elseif s1 = '7' then
				stang_text := 'เจ็ด';
			elseif s1 = '8' then
				stang_text := 'แปด';
			else
				stang_text := 'เก้า';
			end if;
			stang_text := stang_text || 'สิบ';
			
			if s2 = '1' then
				if s1 <> '0' then
					stang_text := stang_text || 'เอ็ด' ;
				else
					stang_text := 'หนึ่ง';
				end if;
			elseif s2 = '2' then
				stang_text := stang_text || 'สอง' ;
			elseif s2 = '3' then
				stang_text := stang_text || 'สาม' ;
			elseif s2 = '4' then
				stang_text := stang_text || 'สี่' ;
			elseif s2 = '5' then
				stang_text := stang_text || 'ห้า' ;
			elseif s2 = '6' then
				stang_text := stang_text || 'หก' ;
			elseif s2 = '7' then
				stang_text := stang_text || 'เจ็ด' ;
			elseif s2 = '8' then
				stang_text := stang_text || 'แปด' ;
			elseif s2 = '9' then
				stang_text := stang_text || 'เก้า' ;
			end if;
		end if;

		if length(batharray[1]) = 1 then
			ba[0] := substring(batharray[1],1,1);
			if ba[0]  = 1 then
				bath_text := 'หนึ่ง';
			elseif ba[0]  = 2 then
				bath_text := 'สอง';
			elseif ba[0]  = 3 then
				bath_text := 'สาม';
			elseif ba[0]  = 4 then
				bath_text := 'สี่';
			elseif ba[0]  = 5 then
				bath_text := 'ห้า';
			elseif ba[0]  = 6 then
				bath_text := 'หก';
			elseif ba[0]  = 7 then
				bath_text := 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text := 'แปด';
			elseif ba[0]  = 9 then
				bath_text := 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 2 then
			ba[0] := substring(batharray[1],2,1);
			ba[1] := substring(batharray[1],1,1);			
			if ba[1]  = 1 then
				bath_text = 'สิบ';
			elseif ba[1]  = 2 then
				bath_text := 'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := 'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 3 then
			ba[0] := substring(batharray[1],3,1);
			ba[1] := substring(batharray[1],2,1);
			ba[2] := substring(batharray[1],1,1);
			
			if ba[2]  = 1 then
				bath_text = 'หนึ่งร้อย';
			elseif ba[2]  = 2 then
				bath_text := 'สองร้อย'   ;
			elseif ba[2]  = 3 then
				bath_text := 'สามร้อย'  ; 
			elseif ba[2]  = 4 then
				bath_text := 'สี่ร้อย'  ;
			elseif ba[2]  = 5 then
				bath_text := 'ห้าร้อย'  ;
			elseif ba[2]  = 6 then
				bath_text := 'หกร้อย' ;
			elseif ba[2]  = 7 then
				bath_text := 'เจ็ดร้อย' ;
			elseif ba[2]  = 8 then
				bath_text := 'แปดร้อย' ;
			elseif ba[2]  = 9 then
				bath_text := 'เก้าร้อย' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[1]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[1]  = 2 then
				bath_text :=bath_text ||  'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := bath_text ||  'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := bath_text || 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := bath_text || 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := bath_text || 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := bath_text || 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := bath_text || 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := bath_text || 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 4 then
			ba[0] := substring(batharray[1],4,1);
			ba[1] := substring(batharray[1],3,1);
			ba[2] := substring(batharray[1],2,1);
			ba[3] := substring(batharray[1],1,1);

			if ba[3]  = 1 then
				bath_text = 'หนึ่งพัน';
			elseif ba[3]  = 2 then
				bath_text := 'สองพัน'   ;
			elseif ba[3]  = 3 then
				bath_text := 'สามพัน'  ; 
			elseif ba[3]  = 4 then
				bath_text := 'สี่พ้น'  ;
			elseif ba[3]  = 5 then
				bath_text := 'ห้าพ้น'  ;
			elseif ba[3]  = 6 then
				bath_text := 'หกพ้น' ;
			elseif ba[3]  = 7 then
				bath_text := 'เจ็ดพ้น' ;
			elseif ba[3]  = 8 then
				bath_text := 'แปดพ้น' ;
			elseif ba[3]  = 9 then
				bath_text := 'เก้าพ้น' ;
			else
				bath_text := bath_text || '';
			end if;			
			if ba[2]  = 1 then
				bath_text = bath_text || 'หนึ่งร้อย';
			elseif ba[2]  = 2 then
				bath_text := bath_text || 'สองร้อย'   ;
			elseif ba[2]  = 3 then
				bath_text := bath_text || 'สามร้อย'  ; 
			elseif ba[2]  = 4 then
				bath_text := bath_text || 'สี่ร้อย'  ;
			elseif ba[2]  = 5 then
				bath_text := bath_text || 'ห้าร้อย'  ;
			elseif ba[2]  = 6 then
				bath_text := bath_text || 'หกร้อย' ;
			elseif ba[2]  = 7 then
				bath_text := bath_text || 'เจ็ดร้อย' ;
			elseif ba[2]  = 8 then
				bath_text := bath_text || 'แปดร้อย' ;
			elseif ba[2]  = 9 then
				bath_text := bath_text || 'เก้าร้อย' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[1]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[1]  = 2 then
				bath_text :=bath_text ||  'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := bath_text ||  'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := bath_text || 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := bath_text || 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := bath_text || 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := bath_text || 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := bath_text || 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := bath_text || 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 5 then
			ba[0] := substring(batharray[1],5,1);
			ba[1] := substring(batharray[1],4,1);
			ba[2] := substring(batharray[1],3,1);
			ba[3] := substring(batharray[1],2,1);
			ba[4] := substring(batharray[1],1,1);

			if ba[4]  = 1 then
				bath_text = 'หนึ่งหมื่น';
			elseif ba[4]  = 2 then
				bath_text := 'สองหมื่น'   ;
			elseif ba[4]  = 3 then
				bath_text := 'สามหมื่น'  ; 
			elseif ba[4]  = 4 then
				bath_text := 'สี่หมื่น'  ;
			elseif ba[4]  = 5 then
				bath_text := 'ห้าหมื่น'  ;
			elseif ba[4]  = 6 then
				bath_text := 'หกหมื่น' ;
			elseif ba[4]  = 7 then
				bath_text := 'เจ็ดหมื่น' ;
			elseif ba[4]  = 8 then
				bath_text := 'แปดหมื่น' ;
			elseif ba[4]  = 9 then
				bath_text := 'เก้าหมื่น' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[3]  = 1 then
				bath_text = bath_text || 'หนึ่งพัน';
			elseif ba[3]  = 2 then
				bath_text :=  bath_text || 'สองพัน'   ;
			elseif ba[3]  = 3 then
				bath_text :=  bath_text || 'สามพัน'  ; 
			elseif ba[3]  = 4 then
				bath_text :=  bath_text || 'สี่พ้น'  ;
			elseif ba[3]  = 5 then
				bath_text :=  bath_text || 'ห้าพ้น'  ;
			elseif ba[3]  = 6 then
				bath_text :=  bath_text || 'หกพ้น' ;
			elseif ba[3]  = 7 then
				bath_text :=  bath_text || 'เจ็ดพ้น' ;
			elseif ba[3]  = 8 then
				bath_text :=  bath_text || 'แปดพ้น' ;
			elseif ba[3]  = 9 then
				bath_text :=  bath_text || 'เก้าพ้น' ;
			else
				bath_text := bath_text || '';
			end if;			
			if ba[2]  = 1 then
				bath_text = bath_text || 'หนึ่งร้อย';
			elseif ba[2]  = 2 then
				bath_text := bath_text || 'สองร้อย'   ;
			elseif ba[2]  = 3 then
				bath_text := bath_text || 'สามร้อย'  ; 
			elseif ba[2]  = 4 then
				bath_text := bath_text || 'สี่ร้อย'  ;
			elseif ba[2]  = 5 then
				bath_text := bath_text || 'ห้าร้อย'  ;
			elseif ba[2]  = 6 then
				bath_text := bath_text || 'หกร้อย' ;
			elseif ba[2]  = 7 then
				bath_text := bath_text || 'เจ็ดร้อย' ;
			elseif ba[2]  = 8 then
				bath_text := bath_text || 'แปดร้อย' ;
			elseif ba[2]  = 9 then
				bath_text := bath_text || 'เก้าร้อย' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[1]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[1]  = 2 then
				bath_text :=bath_text ||  'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := bath_text ||  'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := bath_text || 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := bath_text || 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := bath_text || 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := bath_text || 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := bath_text || 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := bath_text || 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 6 then
			ba[0] := substring(batharray[1],6,1);
			ba[1] := substring(batharray[1],5,1);
			ba[2] := substring(batharray[1],4,1);
			ba[3] := substring(batharray[1],3,1);
			ba[4] := substring(batharray[1],2,1);
			ba[5] := substring(batharray[1],1,1);

			if ba[5]  = 1 then
				bath_text = 'หนึ่งแสน';
			elseif ba[5]  = 2 then
				bath_text := 'สองแสน'   ;
			elseif ba[5]  = 3 then
				bath_text := 'สามแสน'  ; 
			elseif ba[5]  = 4 then
				bath_text := 'สี่แสน'  ;
			elseif ba[5]  = 5 then
				bath_text := 'ห้าแสน'  ;
			elseif ba[5]  = 6 then
				bath_text := 'หกแสน' ;
			elseif ba[5]  = 7 then
				bath_text := 'เจ็ดแสน' ;
			elseif ba[5]  = 8 then
				bath_text := 'แปดแสน' ;
			elseif ba[5]  = 9 then
				bath_text := 'เก้าแสน' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[4]  = 1 then
				bath_text = bath_text || 'หนึ่งหมื่น';
			elseif ba[4]  = 2 then
				bath_text := bath_text || 'สองหมื่น'   ;
			elseif ba[4]  = 3 then
				bath_text := bath_text || 'สามหมื่น'  ; 
			elseif ba[4]  = 4 then
				bath_text := bath_text || 'สี่หมื่น'  ;
			elseif ba[4]  = 5 then
				bath_text := bath_text || 'ห้าหมื่น'  ;
			elseif ba[4]  = 6 then
				bath_text := bath_text || 'หกหมื่น' ;
			elseif ba[4]  = 7 then
				bath_text := bath_text || 'เจ็ดหมื่น' ;
			elseif ba[4]  = 8 then
				bath_text := bath_text || 'แปดหมื่น' ;
			elseif ba[4]  = 9 then
				bath_text := bath_text || 'เก้าหมื่น' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[3]  = 1 then
				bath_text = bath_text || 'หนึ่งพัน';
			elseif ba[3]  = 2 then
				bath_text :=  bath_text || 'สองพัน'   ;
			elseif ba[3]  = 3 then
				bath_text :=  bath_text || 'สามพัน'  ; 
			elseif ba[3]  = 4 then
				bath_text :=  bath_text || 'สี่พ้น'  ;
			elseif ba[3]  = 5 then
				bath_text :=  bath_text || 'ห้าพ้น'  ;
			elseif ba[3]  = 6 then
				bath_text :=  bath_text || 'หกพ้น' ;
			elseif ba[3]  = 7 then
				bath_text :=  bath_text || 'เจ็ดพ้น' ;
			elseif ba[3]  = 8 then
				bath_text :=  bath_text || 'แปดพ้น' ;
			elseif ba[3]  = 9 then
				bath_text :=  bath_text || 'เก้าพ้น' ;
			else
				bath_text := bath_text || '';
			end if;			
			if ba[2]  = 1 then
				bath_text = bath_text || 'หนึ่งร้อย';
			elseif ba[2]  = 2 then
				bath_text := bath_text || 'สองร้อย'   ;
			elseif ba[2]  = 3 then
				bath_text := bath_text || 'สามร้อย'  ; 
			elseif ba[2]  = 4 then
				bath_text := bath_text || 'สี่ร้อย'  ;
			elseif ba[2]  = 5 then
				bath_text := bath_text || 'ห้าร้อย'  ;
			elseif ba[2]  = 6 then
				bath_text := bath_text || 'หกร้อย' ;
			elseif ba[2]  = 7 then
				bath_text := bath_text || 'เจ็ดร้อย' ;
			elseif ba[2]  = 8 then
				bath_text := bath_text || 'แปดร้อย' ;
			elseif ba[2]  = 9 then
				bath_text := bath_text || 'เก้าร้อย' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[1]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[1]  = 2 then
				bath_text :=bath_text ||  'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := bath_text ||  'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := bath_text || 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := bath_text || 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := bath_text || 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := bath_text || 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := bath_text || 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := bath_text || 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 7 then
			ba[0] := substring(batharray[1],7,1);
			ba[1] := substring(batharray[1],6,1);
			ba[2] := substring(batharray[1],5,1);
			ba[3] := substring(batharray[1],4,1);
			ba[4] := substring(batharray[1],3,1);
			ba[5] := substring(batharray[1],2,1);
			ba[6] := substring(batharray[1],1,1);

			if ba[6]  = 1 then
				bath_text = 'หนึ่งล้าน';
			elseif ba[6]  = 2 then
				bath_text := 'สองล้าน'   ;
			elseif ba[6]  = 3 then
				bath_text := 'สามล้าน'  ; 
			elseif ba[6]  = 4 then
				bath_text := 'สี่ล้าน'  ;
			elseif ba[6]  = 5 then
				bath_text := 'ห้าล้าน'  ;
			elseif ba[6]  = 6 then
				bath_text := 'หกล้าน' ;
			elseif ba[6]  = 7 then
				bath_text := 'เจ็ดล้าน' ;
			elseif ba[6]  = 8 then
				bath_text := 'แปดล้าน' ;
			elseif ba[6]  = 9 then
				bath_text := 'เก้าล้าน' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[5]  = 1 then
				bath_text = bath_text || 'หนึ่งแสน';
			elseif ba[5]  = 2 then
				bath_text := bath_text || 'สองแสน'   ;
			elseif ba[5]  = 3 then
				bath_text := bath_text ||  'สามแสน'  ; 
			elseif ba[5]  = 4 then
				bath_text := bath_text || 'สี่แสน'  ;
			elseif ba[5]  = 5 then
				bath_text := bath_text || 'ห้าแสน'  ;
			elseif ba[5]  = 6 then
				bath_text := bath_text || 'หกแสน' ;
			elseif ba[5]  = 7 then
				bath_text := bath_text || 'เจ็ดแสน' ;
			elseif ba[5]  = 8 then
				bath_text := bath_text || 'แปดแสน' ;
			elseif ba[5]  = 9 then
				bath_text := bath_text || 'เก้าแสน' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[4]  = 1 then
				bath_text = bath_text || 'หนึ่งหมื่น';
			elseif ba[4]  = 2 then
				bath_text := bath_text || 'สองหมื่น'   ;
			elseif ba[4]  = 3 then
				bath_text := bath_text || 'สามหมื่น'  ; 
			elseif ba[4]  = 4 then
				bath_text := bath_text || 'สี่หมื่น'  ;
			elseif ba[4]  = 5 then
				bath_text := bath_text || 'ห้าหมื่น'  ;
			elseif ba[4]  = 6 then
				bath_text := bath_text || 'หกหมื่น' ;
			elseif ba[4]  = 7 then
				bath_text := bath_text || 'เจ็ดหมื่น' ;
			elseif ba[4]  = 8 then
				bath_text := bath_text || 'แปดหมื่น' ;
			elseif ba[4]  = 9 then
				bath_text := bath_text || 'เก้าหมื่น' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[3]  = 1 then
				bath_text = bath_text || 'หนึ่งพัน';
			elseif ba[3]  = 2 then
				bath_text :=  bath_text || 'สองพัน'   ;
			elseif ba[3]  = 3 then
				bath_text :=  bath_text || 'สามพัน'  ; 
			elseif ba[3]  = 4 then
				bath_text :=  bath_text || 'สี่พ้น'  ;
			elseif ba[3]  = 5 then
				bath_text :=  bath_text || 'ห้าพ้น'  ;
			elseif ba[3]  = 6 then
				bath_text :=  bath_text || 'หกพ้น' ;
			elseif ba[3]  = 7 then
				bath_text :=  bath_text || 'เจ็ดพ้น' ;
			elseif ba[3]  = 8 then
				bath_text :=  bath_text || 'แปดพ้น' ;
			elseif ba[3]  = 9 then
				bath_text :=  bath_text || 'เก้าพ้น' ;
			else
				bath_text := bath_text || '';
			end if;			
			if ba[2]  = 1 then
				bath_text = bath_text || 'หนึ่งร้อย';
			elseif ba[2]  = 2 then
				bath_text := bath_text || 'สองร้อย'   ;
			elseif ba[2]  = 3 then
				bath_text := bath_text || 'สามร้อย'  ; 
			elseif ba[2]  = 4 then
				bath_text := bath_text || 'สี่ร้อย'  ;
			elseif ba[2]  = 5 then
				bath_text := bath_text || 'ห้าร้อย'  ;
			elseif ba[2]  = 6 then
				bath_text := bath_text || 'หกร้อย' ;
			elseif ba[2]  = 7 then
				bath_text := bath_text || 'เจ็ดร้อย' ;
			elseif ba[2]  = 8 then
				bath_text := bath_text || 'แปดร้อย' ;
			elseif ba[2]  = 9 then
				bath_text := bath_text || 'เก้าร้อย' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[1]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[1]  = 2 then
				bath_text :=bath_text ||  'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := bath_text ||  'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := bath_text || 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := bath_text || 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := bath_text || 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := bath_text || 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := bath_text || 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := bath_text || 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 8 then
			ba[0] := substring(batharray[1],8,1);
			ba[1] := substring(batharray[1],7,1);
			ba[2] := substring(batharray[1],6,1);
			ba[3] := substring(batharray[1],5,1);
			ba[4] := substring(batharray[1],4,1);
			ba[5] := substring(batharray[1],3,1);
			ba[6] := substring(batharray[1],2,1);
			ba[7] := substring(batharray[1],1,1);

			if ba[7]  = 1 then
				bath_text = 'สิบ';
			elseif ba[7]  = 2 then
				bath_text := 'ยี่สิบ'   ;
			elseif ba[7]  = 3 then
				bath_text := 'สามสิบ'  ; 
			elseif ba[7]  = 4 then
				bath_text := 'สี่สิบ'  ;
			elseif ba[7]  = 5 then
				bath_text := 'ห้าสิบ'  ;
			elseif ba[7]  = 6 then
				bath_text := 'หกสิบ' ;
			elseif ba[7]  = 7 then
				bath_text := 'เจ็ดสิบ' ;
			elseif ba[7]  = 8 then
				bath_text := 'แปดสิบ' ;
			elseif ba[7]  = 9 then
				bath_text := 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[6]  = 1 then
				if ba[7] <> 0 then
					bath_text = bath_text || 'เอ็ดล้าน';
				else
					bath_text = bath_text || 'หนึ่งล้าน';
				end if;
			elseif ba[6]  = 2 then
				bath_text := bath_text || 'สองล้าน'   ;
			elseif ba[6]  = 3 then
				bath_text := bath_text || 'สามล้าน'  ; 
			elseif ba[6]  = 4 then
				bath_text := bath_text || 'สี่ล้าน'  ;
			elseif ba[6]  = 5 then
				bath_text := bath_text || 'ห้าล้าน'  ;
			elseif ba[6]  = 6 then
				bath_text := bath_text || 'หกล้าน' ;
			elseif ba[6]  = 7 then
				bath_text := bath_text || 'เจ็ดล้าน' ;
			elseif ba[6]  = 8 then
				bath_text := bath_text || 'แปดล้าน' ;
			elseif ba[6]  = 9 then
				bath_text := bath_text || 'เก้าล้าน' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[5]  = 1 then
				bath_text = bath_text || 'หนึ่งแสน';
			elseif ba[5]  = 2 then
				bath_text := bath_text || 'สองแสน'   ;
			elseif ba[5]  = 3 then
				bath_text := bath_text ||  'สามแสน'  ; 
			elseif ba[5]  = 4 then
				bath_text := bath_text || 'สี่แสน'  ;
			elseif ba[5]  = 5 then
				bath_text := bath_text || 'ห้าแสน'  ;
			elseif ba[5]  = 6 then
				bath_text := bath_text || 'หกแสน' ;
			elseif ba[5]  = 7 then
				bath_text := bath_text || 'เจ็ดแสน' ;
			elseif ba[5]  = 8 then
				bath_text := bath_text || 'แปดแสน' ;
			elseif ba[5]  = 9 then
				bath_text := bath_text || 'เก้าแสน' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[4]  = 1 then
				bath_text = bath_text || 'หนึ่งหมื่น';
			elseif ba[4]  = 2 then
				bath_text := bath_text || 'สองหมื่น'   ;
			elseif ba[4]  = 3 then
				bath_text := bath_text || 'สามหมื่น'  ; 
			elseif ba[4]  = 4 then
				bath_text := bath_text || 'สี่หมื่น'  ;
			elseif ba[4]  = 5 then
				bath_text := bath_text || 'ห้าหมื่น'  ;
			elseif ba[4]  = 6 then
				bath_text := bath_text || 'หกหมื่น' ;
			elseif ba[4]  = 7 then
				bath_text := bath_text || 'เจ็ดหมื่น' ;
			elseif ba[4]  = 8 then
				bath_text := bath_text || 'แปดหมื่น' ;
			elseif ba[4]  = 9 then
				bath_text := bath_text || 'เก้าหมื่น' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[3]  = 1 then
				bath_text = bath_text || 'หนึ่งพัน';
			elseif ba[3]  = 2 then
				bath_text :=  bath_text || 'สองพัน'   ;
			elseif ba[3]  = 3 then
				bath_text :=  bath_text || 'สามพัน'  ; 
			elseif ba[3]  = 4 then
				bath_text :=  bath_text || 'สี่พ้น'  ;
			elseif ba[3]  = 5 then
				bath_text :=  bath_text || 'ห้าพ้น'  ;
			elseif ba[3]  = 6 then
				bath_text :=  bath_text || 'หกพ้น' ;
			elseif ba[3]  = 7 then
				bath_text :=  bath_text || 'เจ็ดพ้น' ;
			elseif ba[3]  = 8 then
				bath_text :=  bath_text || 'แปดพ้น' ;
			elseif ba[3]  = 9 then
				bath_text :=  bath_text || 'เก้าพ้น' ;
			else
				bath_text := bath_text || '';
			end if;			
			if ba[2]  = 1 then
				bath_text = bath_text || 'หนึ่งร้อย';
			elseif ba[2]  = 2 then
				bath_text := bath_text || 'สองร้อย'   ;
			elseif ba[2]  = 3 then
				bath_text := bath_text || 'สามร้อย'  ; 
			elseif ba[2]  = 4 then
				bath_text := bath_text || 'สี่ร้อย'  ;
			elseif ba[2]  = 5 then
				bath_text := bath_text || 'ห้าร้อย'  ;
			elseif ba[2]  = 6 then
				bath_text := bath_text || 'หกร้อย' ;
			elseif ba[2]  = 7 then
				bath_text := bath_text || 'เจ็ดร้อย' ;
			elseif ba[2]  = 8 then
				bath_text := bath_text || 'แปดร้อย' ;
			elseif ba[2]  = 9 then
				bath_text := bath_text || 'เก้าร้อย' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[1]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[1]  = 2 then
				bath_text :=bath_text ||  'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := bath_text ||  'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := bath_text || 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := bath_text || 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := bath_text || 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := bath_text || 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := bath_text || 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := bath_text || 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;
		elseif length(batharray[1]) = 9 then
			ba[0] := substring(batharray[1],9,1);
			ba[1] := substring(batharray[1],8,1);
			ba[2] := substring(batharray[1],7,1);
			ba[3] := substring(batharray[1],6,1);
			ba[4] := substring(batharray[1],5,1);
			ba[5] := substring(batharray[1],4,1);
			ba[6] := substring(batharray[1],3,1);
			ba[7] := substring(batharray[1],2,1);
			ba[8] := substring(batharray[1],1,1);

			if ba[8]  = 1 then
				bath_text =  'หนึ่งร้อย';
			elseif ba[8]  = 2 then
				bath_text :=  'สองร้อย'   ;
			elseif ba[8]  = 3 then
				bath_text := 'สามร้อย'  ; 
			elseif ba[8]  = 4 then
				bath_text := 'สี่ร้อย'  ;
			elseif ba[8]  = 5 then
				bath_text := 'ห้าร้อย'  ;
			elseif ba[8]  = 6 then
				bath_text := 'หกร้อย' ;
			elseif ba[8]  = 7 then
				bath_text :=  'เจ็ดร้อย' ;
			elseif ba[8]  = 8 then
				bath_text :=  'แปดร้อย' ;
			elseif ba[8]  = 9 then
				bath_text :=  'เก้าร้อย' ;
			else
				bath_text :=  '';
			end if;
			if ba[7]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[7]  = 2 then
				bath_text := bath_text ||'ยี่สิบ'   ;
			elseif ba[7]  = 3 then
				bath_text := bath_text ||'สามสิบ'  ; 
			elseif ba[7]  = 4 then
				bath_text := bath_text ||'สี่สิบ'  ;
			elseif ba[7]  = 5 then
				bath_text := bath_text ||'ห้าสิบ'  ;
			elseif ba[7]  = 6 then
				bath_text := bath_text ||'หกสิบ' ;
			elseif ba[7]  = 7 then
				bath_text := bath_text ||'เจ็ดสิบ' ;
			elseif ba[7]  = 8 then
				bath_text := bath_text ||'แปดสิบ' ;
			elseif ba[7]  = 9 then
				bath_text := bath_text ||'เก้าสิบ' ;
			else
				bath_text := bath_text ||'';
			end if;	
			if ba[6]  = 1 then
				if ba[7] <> 0 then
					bath_text = bath_text || 'เอ็ดล้าน';
				else
					bath_text = bath_text || 'หนึ่งล้าน';
				end if;
			elseif ba[6]  = 2 then
				bath_text := bath_text || 'สองล้าน'   ;
			elseif ba[6]  = 3 then
				bath_text := bath_text || 'สามล้าน'  ; 
			elseif ba[6]  = 4 then
				bath_text := bath_text || 'สี่ล้าน'  ;
			elseif ba[6]  = 5 then
				bath_text := bath_text || 'ห้าล้าน'  ;
			elseif ba[6]  = 6 then
				bath_text := bath_text || 'หกล้าน' ;
			elseif ba[6]  = 7 then
				bath_text := bath_text || 'เจ็ดล้าน' ;
			elseif ba[6]  = 8 then
				bath_text := bath_text || 'แปดล้าน' ;
			elseif ba[6]  = 9 then
				bath_text := bath_text || 'เก้าล้าน' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[5]  = 1 then
				bath_text = bath_text || 'หนึ่งแสน';
			elseif ba[5]  = 2 then
				bath_text := bath_text || 'สองแสน'   ;
			elseif ba[5]  = 3 then
				bath_text := bath_text ||  'สามแสน'  ; 
			elseif ba[5]  = 4 then
				bath_text := bath_text || 'สี่แสน'  ;
			elseif ba[5]  = 5 then
				bath_text := bath_text || 'ห้าแสน'  ;
			elseif ba[5]  = 6 then
				bath_text := bath_text || 'หกแสน' ;
			elseif ba[5]  = 7 then
				bath_text := bath_text || 'เจ็ดแสน' ;
			elseif ba[5]  = 8 then
				bath_text := bath_text || 'แปดแสน' ;
			elseif ba[5]  = 9 then
				bath_text := bath_text || 'เก้าแสน' ;
			else
				bath_text := bath_text || '';
			end if;	
			if ba[4]  = 1 then
				bath_text = bath_text || 'หนึ่งหมื่น';
			elseif ba[4]  = 2 then
				bath_text := bath_text || 'สองหมื่น'   ;
			elseif ba[4]  = 3 then
				bath_text := bath_text || 'สามหมื่น'  ; 
			elseif ba[4]  = 4 then
				bath_text := bath_text || 'สี่หมื่น'  ;
			elseif ba[4]  = 5 then
				bath_text := bath_text || 'ห้าหมื่น'  ;
			elseif ba[4]  = 6 then
				bath_text := bath_text || 'หกหมื่น' ;
			elseif ba[4]  = 7 then
				bath_text := bath_text || 'เจ็ดหมื่น' ;
			elseif ba[4]  = 8 then
				bath_text := bath_text || 'แปดหมื่น' ;
			elseif ba[4]  = 9 then
				bath_text := bath_text || 'เก้าหมื่น' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[3]  = 1 then
				bath_text = bath_text || 'หนึ่งพัน';
			elseif ba[3]  = 2 then
				bath_text :=  bath_text || 'สองพัน'   ;
			elseif ba[3]  = 3 then
				bath_text :=  bath_text || 'สามพัน'  ; 
			elseif ba[3]  = 4 then
				bath_text :=  bath_text || 'สี่พ้น'  ;
			elseif ba[3]  = 5 then
				bath_text :=  bath_text || 'ห้าพ้น'  ;
			elseif ba[3]  = 6 then
				bath_text :=  bath_text || 'หกพ้น' ;
			elseif ba[3]  = 7 then
				bath_text :=  bath_text || 'เจ็ดพ้น' ;
			elseif ba[3]  = 8 then
				bath_text :=  bath_text || 'แปดพ้น' ;
			elseif ba[3]  = 9 then
				bath_text :=  bath_text || 'เก้าพ้น' ;
			else
				bath_text := bath_text || '';
			end if;			
			if ba[2]  = 1 then
				bath_text = bath_text || 'หนึ่งร้อย';
			elseif ba[2]  = 2 then
				bath_text := bath_text || 'สองร้อย'   ;
			elseif ba[2]  = 3 then
				bath_text := bath_text || 'สามร้อย'  ; 
			elseif ba[2]  = 4 then
				bath_text := bath_text || 'สี่ร้อย'  ;
			elseif ba[2]  = 5 then
				bath_text := bath_text || 'ห้าร้อย'  ;
			elseif ba[2]  = 6 then
				bath_text := bath_text || 'หกร้อย' ;
			elseif ba[2]  = 7 then
				bath_text := bath_text || 'เจ็ดร้อย' ;
			elseif ba[2]  = 8 then
				bath_text := bath_text || 'แปดร้อย' ;
			elseif ba[2]  = 9 then
				bath_text := bath_text || 'เก้าร้อย' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[1]  = 1 then
				bath_text = bath_text || 'สิบ';
			elseif ba[1]  = 2 then
				bath_text :=bath_text ||  'ยี่สิบ'   ;
			elseif ba[1]  = 3 then
				bath_text := bath_text ||  'สามสิบ'  ; 
			elseif ba[1]  = 4 then
				bath_text := bath_text || 'สี่สิบ'  ;
			elseif ba[1]  = 5 then
				bath_text := bath_text || 'ห้าสิบ'  ;
			elseif ba[1]  = 6 then
				bath_text := bath_text || 'หกสิบ' ;
			elseif ba[1]  = 7 then
				bath_text := bath_text || 'เจ็ดสิบ' ;
			elseif ba[1]  = 8 then
				bath_text := bath_text || 'แปดสิบ' ;
			elseif ba[1]  = 9 then
				bath_text := bath_text || 'เก้าสิบ' ;
			else
				bath_text := bath_text || '';
			end if;
			if ba[0]  = 1 then
				if ba[1] <> 0 then
					bath_text := bath_text || 'เอ็ด';
				else
					bath_text :=  bath_text || 'หนึ่ง';
				end if;
			elseif ba[0]  = 2 then
				bath_text :=  bath_text || 'สอง';
			elseif ba[0]  = 3 then
				bath_text :=  bath_text || 'สาม';
			elseif ba[0]  = 4 then
				bath_text :=  bath_text || 'สี่';
			elseif ba[0]  = 5 then
				bath_text :=  bath_text || 'ห้า';
			elseif ba[0]  = 6 then
				bath_text :=  bath_text || 'หก';
			elseif ba[0]  = 7 then
				bath_text :=  bath_text || 'เจ็ด';
			elseif ba[0]  = 8 then
				bath_text :=  bath_text || 'แปด';
			elseif ba[0]  = 9 then
				bath_text :=  bath_text || 'เก้า';
			else
				bath_text := bath_text || '';
			end if;

		end if;		


		if  length(batharray[1])  = 1 and length(bath_text) = 0 then
			bath_text := bath_text || '';
		else
			bath_text := bath_text || 'บาท';
		end if;
		if length(bath_text) = 0 and length(stang_text) = 0 then
			RETURN '';
		else
			RETURN bath_text || stang_text || subtext;
		end if;
       END;
$$ LANGUAGE plpgsql;
