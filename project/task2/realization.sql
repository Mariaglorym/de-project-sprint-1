-- добавьте код сюда
CREATE OR REPLACE VIEW analysis.Orders AS 
select o.order_id, o.order_ts, o.user_id, o.bonus_payment, o.payment, o."cost", o.bonus_grant, f_ls.status 
from production.orders o
left join 
  (select order_id, last_status as status from(
  select order_id,
  FIRST_VALUE(status_id) OVER(PARTITION BY order_id ORDER BY dttm desc) as last_status
  from production.orderstatuslog
   ) p_ls 
  group by order_id, last_status) f_ls on f_ls.order_id =o.order_id)