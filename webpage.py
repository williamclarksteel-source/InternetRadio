def webpage(temperature, state, station):
    html = f'''
            <!DOCTYPE html>
            <html>            
            <body style=background-color:#767676;color:#F9F9F9;>
            <h1 style=background-image:linear-gradient(#323232,#5F5F5F);text-align:center;font-size:32px;padding:50px>Radio Web Control Panel</h1>
            <p>LED: {state}</p>
            <p>Temperature is {temperature}</p>
            <p>Currently Playing {station}</p?
            <div>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <form action="./nextstation">
            <input type="submit" value="Next Station" />
            </form>
            </form>
            <form action="./prevstation">
            <input type="submit" value="Previous Station" />
            </form>
            <form action="./close">
            <input type="submit" value="Stop server" />
            </form>
            </body>
            </html>
            '''
    return str(html)