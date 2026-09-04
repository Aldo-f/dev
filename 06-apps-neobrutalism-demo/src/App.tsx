import { Avatar } from "@/components/ui/avatar";
import { AvatarImage } from "@/components/ui/avatar-image";
import { AvatarFallback } from "@/components/ui/avatar-fallback";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function App() {
  return (
    <div className="min-h-screen bg-background p-8 space-y-12">
      <header className="text-center">
        <div className="inline-flex items-center space-x-4">
          <Avatar className="h-20 w-20">
            <AvatarImage src="https://github.com/aldo-f.png" alt="Aldo Fieuw" />
            <AvatarFallback>AF</AvatarFallback>
          </Avatar>
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Aldo Fieuw
            </h1>
            <p className="text-muted-foreground">
              Infrastructure Engineer & Full-Stack Developer
            </p>
          </div>
        </div>
        <p className="mt-4 max-w-2xl mx-auto text-muted-foreground">
          Passionate about building reliable, observable systems and crafting 
          thoughtful user experiences. Specializing in home lab automation, 
          cloud-native applications, and developer tooling.
        </p>
      </header>

      <div className="h-px bg-border"></div>

      <section>
        <h2 className="text-2xl font-bold mb-6 text-foreground">About Me</h2>
        <p className="text-muted-foreground">
          I specialize in designing and maintaining self-hosted infrastructure 
          using Ansible, Docker, and Kubernetes. My work focuses on creating 
          resilient, observable systems that run smoothly on Raspberry Pi hardware.
          When not optimizing home labs, I build full-stack applications with 
          React, Node.js, and Python, always prioritizing developer experience 
          and system reliability.
        </p>
        <div className="mt-6 flex flex-wrap gap-4">
          <Badge variant="secondary">Home Lab</Badge>
          <Badge variant="secondary">DevOps</Badge>
          <Badge variant="secondary">Full-Stack</Badge>
          <Badge variant="secondary">TypeScript</Badge>
          <Badge variant="secondary">Python</Badge>
          <Badge variant="secondary">Docker</Badge>
          <Badge variant="secondary">Ansible</Badge>
          <Badge variant="secondary">React</Badge>
        </div>
      </section>

      <div className="h-px bg-border"></div>

      <section>
        <h2 className="text-2xl font-bold mb-6 text-foreground">Featured Projects</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-foreground">Home Lab Infrastructure</CardTitle>
              <CardDescription>
                Ansible-managed Raspberry Pi 5 cluster running Traefik, Jellyfin, 
                Vaultwarden, and custom applications.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <p className="text-muted-foreground">
                • 15+ containerized services<br />
                • Zero-downtime deployments<br />
                • Monitoring with Prometheus & Grafana<br />
                • Automated backups to encrypted storage
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" size="sm" asChild>
                <a href="https://github.com/aldo-f/home-lab" target="_blank" rel="noreferrer">
                  View Source
                </a>
              </Button>
            </CardFooter>
          </Card>

          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-foreground">Hermes Agent UI</CardTitle>
              <CardDescription>
                Desktop interface for the Hermes AI assistant built with 
                Electron, Vite, and TanStack Start.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <p className="text-muted-foreground">
                • Real-time tool execution<br />
                • Voice input/output<br />
                • Skill-based architecture<br />
                • Cross-platform desktop app
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" size="sm" asChild>
                <a href="https://github.com/aldo-f/hermes-workspace" target="_blank" rel="noreferrer">
                  View Source
                </a>
              </Button>
            </CardFooter>
          </Card>

          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-foreground">FreeLLM API</CardTitle>
              <CardDescription>
                Unified API for accessing multiple LLM providers with 
                automatic failover and load balancing.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <p className="text-muted-foreground">
                • OpenAI-compatible endpoints<br />
                • Provider fallback mechanisms<br />
                • Token usage analytics<br />
                • Dockerized for easy deployment
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" size="sm" asChild>
                <a href="https://github.com/aldo-f/freellmapi" target="_blank" rel="noreferrer">
                  View Source
                </a>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </section>

      <div className="h-px bg-border"></div>

      <section>
        <h2 className="text-2xl font-bold mb-6 text-foreground">Get In Touch</h2>
        <form className="max-w-2xl mx-auto space-y-6">
          <div className="space-y-4">
            <Label htmlFor="name" className="font-medium text-foreground">
              Name
            </Label>
            <Input
              id="name"
              type="text"
              placeholder="Your name"
              required
              className="w-full"
            />
          </div>
          <div className="space-y-4">
            <Label htmlFor="email" className="font-medium text-foreground">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="your@email.com"
              required
              className="w-full"
            />
          </div>
          <div className="space-y-4">
            <Label htmlFor="message" className="font-medium text-foreground">
              Message
            </Label>
            <Textarea
              id="message"
              rows={5}
              placeholder="How can I help you?"
              required
              className="w-full"
            />
          </div>
          <Button variant="default" type="submit" className="w-full">
            Send Message
          </Button>
        </form>
      </section>

      <div className="h-px bg-border"></div>

      <footer className="mt-12 text-center text-muted-foreground">
        <p>
          © {new Date().getFullYear()} Aldo Fieuw. All rights reserved.
        </p>
        <div className="mt-4 flex justify-center space-x-4">
          <Button variant="outline" size="sm" asChild>
            <a href="https://github.com/aldo-f" target="_blank" rel="noreferrer" aria-label="GitHub">
              GitHub
            </a>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <a href="https://gitlab.com/aldo-f" target="_blank" rel="noreferrer" aria-label="GitLab">
              GitLab
            </a>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <a href="https://codepen.io/aldo-f" target="_blank" rel="noreferrer" aria-label="CodePen">
              CodePen
            </a>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <a href="https://linkedin.com/in/aldo-fieuw" target="_blank" rel="noreferrer" aria-label="LinkedIn">
              LinkedIn
            </a>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <a href="https://t.me/aldo_fieuw" target="_blank" rel="noreferrer" aria-label="Telegram">
              Telegram
            </a>
          </Button>
        </div>
      </footer>
    </div>
  );
}