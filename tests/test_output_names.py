from click.testing import CliRunner
from airtable_export.cli import cli
from urllib.parse import quote
import json
import pytest

@pytest.mark.parametrize('fmt,ext',[('json','json'),('yaml','yml'),('ndjson','ndjson')])
@pytest.mark.parametrize('automatic',[False,True])
def test_separator_names_are_distinct_local_files(tmp_path,httpx_mock,fmt,ext,automatic):
    names=['Sales/2026','Sales%2F2026','Sales\\2026','普通名称','plain']
    expected=['Sales%2F2026','Sales%252F2026','Sales%5C2026','普通名称','plain']
    if automatic:
        httpx_mock.add_response(url='https://api.airtable.com/v0/meta/bases/appTest/tables',json={'tables':[{'name':n} for n in names]})
    for i,name in enumerate(names):
        httpx_mock.add_response(url='https://api.airtable.com/v0/appTest/'+quote(name,safe=''),json={'records':[{'id':'rec'+str(i),'createdTime':'2026-01-01','fields':{'value':i}}]})
    args=[str(tmp_path),'appTest']+([] if automatic else names)+['--key','synthetic','--'+fmt]
    result=CliRunner().invoke(cli,args)
    assert result.exit_code==0,repr(result.exception)
    for i,name in enumerate(expected):
        target=tmp_path/(name+'.'+ext)
        assert target.is_file()
        assert 'rec'+str(i) in target.read_text()
    assert not (tmp_path/'Sales').exists()
