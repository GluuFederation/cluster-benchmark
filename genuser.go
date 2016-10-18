package main

import (
	"bytes"
	"flag"
	"fmt"
	"math/rand"
	"strconv"
	"strings"
	"text/template"
	"time"

	"github.com/manveru/faker"
)

const TMPL = `dn: inum={{.inum}},ou=people,o=@!AE1F.6E2B.849B.7678!0001!18E5.E69D,o=gluu
objectClass: gluuPerson
objectClass: top
givenName: {{.fname}}
uid: {{.uid}}
cn: {{.fname}} {{.uid}}
gluuStatus: active
sn: {{.lname}}
userPassword: {SSHA512}b3AjXKcf3Cfjujv96bzQIDZU/MugwXRQJquw5MnFzBJO3B4mkKdHJXmolayDzBruwFAmE58PE4Gaaektx/Ql0sK+yRy9AsCg
mail: {{.uid}}@gluu.org
iname: *person*{{.uid}}
displayName: {{.uid}}
inum: {{.inum}}
`

func random_hex(size int) string {
	if size <= 0 {
		return ""
	}
	strlen := size * 4
	rand.Seed(time.Now().UTC().UnixNano())
	const chars = "A0B1C2D3E4F5678901234A5B6C7D8E9F"
	result := make([]byte, strlen)
	for i := 0; i < strlen; i++ {
		result[i] = chars[rand.Intn(len(chars))]
	}
	rs := []rune(string(result))
	st := []string{}
	for i := 0; i < strlen; i = i + 4 {
		st = append(st, string(rs[i:i+4]))
	}
	return strings.Join(st[:], ".")
}

type datacon struct {
	F4Q  string
	set  map[string]bool
	fake *faker.Faker
}

func (dc *datacon) rand_name() (string, string) {
	return dc.fake.FirstName(), dc.fake.LastName()
}

func (dc *datacon) rand_inum() string {
	var r string
	for {
		r = random_hex(2)
		if dc.set[r] != true {
			dc.set[r] = true
			break
		}
	}
	return "@" + dc.F4Q + "!0001!18E5.E69D!0000!" + r
}

func (dc *datacon) make_data(uid int) map[string]string {
	fname, lname := dc.rand_name()
	data := map[string]string{
		"inum":  dc.rand_inum(),
		"fname": fname,
		"lname": lname,
		"uid":   "user_" + strconv.Itoa(uid),
	}
	return data
}

func main() {
	numbPtr := flag.Int("n", 100, "an int")
	flag.Parse()
	number := *numbPtr
	START := 1000000000
	output_con := []string{}
	fake, err := faker.New("en")
	if err != nil {
		panic(err)
	}
	dc := datacon{
		F4Q:  random_hex(4),
		set:  map[string]bool{},
		fake: fake,
	}
	t := template.Must(template.New("ldap").Parse(TMPL))
	buf := &bytes.Buffer{}
	for uid := START; uid < START+number; uid++ {
		data := dc.make_data(uid)
		if err := t.Execute(buf, data); err != nil {
			panic(err)
		}
		output_con = append(output_con, buf.String())
		buf.Reset()
	}
	for _, entry := range output_con {
		fmt.Println(entry)
	}
	fmt.Println("# Report")
	fmt.Println("# Total entry:", len(dc.set))
}
