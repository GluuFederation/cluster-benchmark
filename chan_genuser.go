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
    //"reflect"

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

func random_hex(rnd *rand.Rand, size int) string {
    if size <= 0 {
        return ""
    }
    strlen := size * 4
    const chars = "A0B1C2D3E4F5678901234A5B6C7D8E9F"
    result := make([]byte, strlen)
    for i := 0; i < strlen; i++ {
        result[i] = chars[rnd.Intn(len(chars))]
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
    fake *faker.Faker
}

func (dc *datacon) rand_name() (string, string) {
    return dc.fake.FirstName(), dc.fake.LastName()
}

func (dc *datacon) rand_inum(rnd *rand.Rand) string {
    r := random_hex(rnd, 2)
    return "@" + dc.F4Q + "!0001!18E5.E69D!0000!" + r
}

func (dc *datacon) make_data(rnd *rand.Rand, uid int) map[string]string {
    fname, lname := dc.rand_name()
    data := map[string]string{
        "inum":  dc.rand_inum(rnd),
        "fname": fname,
        "lname": lname,
        "uid":   "user_" + strconv.Itoa(uid),
    }
    return data
}

func (dc *datacon) render(uid int, end int) chan []string {
    ch := make(chan []string)
    scon := []string{}
    r := rand.New(rand.NewSource(time.Now().UnixNano()))
    r.Seed(time.Now().UnixNano())
    t := template.Must(template.New("ldap").Parse(TMPL))
    buf := &bytes.Buffer{}
    go func() {
        for i := uid; i < end; i++ {
            data := dc.make_data(r, i)
            if err := t.Execute(buf, data); err != nil {
                panic(err)
            }
            scon = append(scon, buf.String())
            buf.Reset()
        }
        ch<-scon
    }()
    return ch
}

func main() {
    numbPtr := flag.Int("n", 100, "an int")
    flag.Parse()
    number := *numbPtr
    START := 1000000000
    SEGMENT := 500000
    fake, err := faker.New("en")
    if err != nil {
        panic(err)
    }
    r := rand.New(rand.NewSource(time.Now().UnixNano()))
    dc := datacon{
        F4Q:  random_hex(r, 4),
        fake: fake,
    }
    bchanchan := []chan []string{}
     
    for uid := START; uid < START+number; uid = uid + SEGMENT {
        if (START+number) - uid < SEGMENT {
            bchanchan = append(bchanchan, dc.render(uid, START+number ))    
        } else {
            bchanchan = append(bchanchan, dc.render(uid, uid+SEGMENT))
        }
    }

    for _, strchans := range bchanchan {
        for _, s := range <-strchans {
            fmt.Println(s)
        }
    }
}
