DECLARE @dts datetime = DATEADD(DAY, -10, GETDATE());

SELECT TOP (1) 
    kb.Content,
    prob.tc_problemnumber
FROM 
    [comdb21vr].[TaxcomAbase_MSCRM_R2016].[dbo].[KbArticleBase] kb WITH (NOLOCK)
JOIN 
    [comdb21vr].[TaxcomAbase_MSCRM_R2016].[dbo].[tc_problemBase] prob ON kb.tc_problem_id = prob.tc_problemId
WHERE 
    kb.StateCode = 3 
    AND kb.tc_is_send_after_publication = 1 
    AND kb.Tc_serviceunitId IN (
	'6CE14654-1876-E911-9D38-005056863AFC', 
	'04D63481-0198-E911-9D38-005056863AFC',
	'63022157-0B9C-E911-9D38-005056863AFC',
	'98D1D185-0D9A-E711-B496-005056863AFC', 
	'9A1427CE-5248-E811-B96E-005056863AFC', 
	'015C1495-FB4C-E711-BE4C-005056863AFC',
	'5DDAA5F8-FB4C-E711-BE4C-005056863AFC', 
	'FCF522BC-0750-E711-BE4C-005056863AFC', 
	'6F2F62C8-0750-E711-BE4C-005056863AFC',
	'454D584F-A0DB-E911-A2DD-005056897AB1', 
	'3DD5C52C-58E8-EA11-A2E1-005056897AB1'
	) 
    AND kb.tc_publication_date > @dts 
ORDER BY 
    kb.tc_publication_date DESC;