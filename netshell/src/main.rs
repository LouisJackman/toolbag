use std::{
    vec::Vec,
    env,
    io::{
        self,
        BufRead,
        BufReader,
        Read,
        Write,
    },
    net::{
        TcpListener,
        TcpStream,
    },
    process::{
        self,
        Command,
    },
    thread,
};

#[derive(Copy, Clone)]
struct Port(u16);

const DEFAULT_PORT: Port = Port(8080);

fn dispatch_clients(
    listener: TcpListener,
    handle_client: &'static (impl Sync + Fn(TcpStream) -> io::Result<()>),
) {
    listener.incoming().for_each(|maybe_client| maybe_client
        .map(|client| {
            thread::spawn(move ||
                handle_client(client)
            );
        })
        .unwrap_or_else(|err| {
            eprintln!(
                "handling an incoming client failed: {}",
                err
            );
        })
    )
}

fn next_input(client: &mut impl Read) -> io::Result<Option<String>> {
    let mut buffered = BufReader::new(client);
    let mut line = String::new();
    let n = buffered.read_line(&mut line)?;

    let result = if n == 0 {
        None
    } else {
        Some(String::from(line.trim_end()))
    };
    Ok(result)
}

#[cfg(not(windows))]
fn new_shell_command(cmd: &str) -> Command {
    let mut result = Command::new("sh");
    result.args(&["-c", cmd]);
    result
}

#[cfg(windows)]
fn new_shell_command(cmd: &str) -> Command {
    let mut result = Command::new("cmd");
    result.args(&["/C", cmd]);
    result
}

fn send_client_cmd_feedback(
    client: &mut TcpStream,
    output: process::Output
) -> io::Result<()> {

    let out = String
        ::from_utf8(output.stdout)
        .unwrap_or_else(|_| String::from("[FAILED TO PARSE AS UTF-8]"));

    let err = String
        ::from_utf8(output.stderr)
        .unwrap_or_else(|_| String::from("[FAILED TO PARSE AS UTF-8]"));

    let msg = match output.status.code() {
        Some(code) => format!(
            concat!(
                "status: {}\n",
                "stdout: {}\n",
                "stderr: {}\n",
            ),
            code,
            out,
            err,
        ),
        None => format!(
            concat!(
                "stdout: {}\n",
                "stderr: {}\n",
            ),
            out,
            err,
        ),
    };

    client.write_all(msg.as_bytes())?;
    client.flush()
}

fn handle_client(mut client: TcpStream) -> io::Result<()> {
    loop {
        client.write_all(b">>> ")?;
        client.flush()?;

        let maybe_cmd = next_input(&mut client)?;
        match maybe_cmd {
            None => break,
            Some(cmd) => {
                if cmd.is_empty() {
                    continue
                }
                println!("Running command `{}`...", cmd);
                let output = new_shell_command(&cmd).output()?;
                send_client_cmd_feedback(&mut client, output)?;
                println!("Finished running command");
            },
        }
    }

    client.write_all(b"\n")?;
    client.flush()?;

    Ok(())
}

fn parse_args() -> Result<Port, &'static str> {
    let args = env::args().collect::<Vec<String>>();

    match args.len() {
        1 => Ok(DEFAULT_PORT),
        2 => args[0]
            .parse()
            .map(Port)
            .map_err(|_| "invalid port number"),
        _ => Err("too many arguments; only 1 port argument needed")?,
    }
}

fn main() -> Result<(), String> {
    let Port(port) = parse_args()?;

    println!("Starting server on port {}.", port);

    let host = format!("0.0.0.0:{}", port);
    let listener = TcpListener
        ::bind(host)
        .map_err(|err| format!("could not bind: {}", err))?;
    dispatch_clients(listener, &handle_client);
    Ok(())
}
