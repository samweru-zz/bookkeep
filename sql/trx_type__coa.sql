select tt.id, tt.cr_id, tt.dr_id, cr.name as credit, dr.name as debit, tt.token 
from books_trxtype tt 
left join books_coa cr on tt.cr_id = cr.id 
left join books_coa dr on tt.dr_id = dr.id;

